"""
User input processing and validation.

Handles different types of user input (usernames, URLs, patterns) and
provides validation, type detection, and URL conversion utilities.
"""

import streamlit as st
import re
from letterboxdpy.constants.project import DOMAIN
from letterboxdpy.utils.utils_url import is_short_url, parse_list_url
from letterboxdpy.utils.utils_validators import is_url


class Input:
    textbox_placeholder = 'Enter a **username**, list **url** or **username/list-title**.'

    def __init__(self):
        self.data = None
        self.type = None
        self.length = None
        self.is_url = None
        self.is_short_url = None

        self.is_alpha = None
        self.is_username = None
        self.is_whitespace = None
        self.is_empty = None

        self.is_numeric = None
        self.is_negative = None
        self.is_positive = None

    def process_data(self):
        query_data = st.query_params.to_dict()

        input_data = st.text_input(
            value=query_data['q'] if 'q' in query_data else '',
            label=self.textbox_placeholder
            )

        if 'q' in query_data:
            input_type = 'query'
        else:
            input_type = 'input' if input_data else None

        st.query_params.clear()

        self.data = input_data
        self.type = input_type
        self.length = len(input_data) if input_data else 0

        self.is_empty = not self.data
        self.is_whitespace = self.data and self.data.isspace()
        self.is_alpha = self.data and self.data.isalpha()
        self.is_numeric = self.data and self.data.isdigit()
        self.is_username = self.data and '/' not in self.data

        self.is_negative = self.is_numeric and int(self.data) < 0
        self.is_positive = self.is_numeric and int(self.data) > 0

        self.is_url = not self.is_username and is_url(self.data)
        self.is_short_url = not self.is_username and is_short_url(self.data)


    @staticmethod
    def convert_to_url(data):
        """
        normal:
            fastfingertips/list_name                              -> fastfingertips/list_name
            fastfingertips/list/list_name                         -> fastfingertips/list_name
            fastfingertips/list/list_name/detail                  -> fastfingertips/list_name

        specific names('list' or 'detail'):
            # if a list's name is 'list'?
            `fastfingertips/list`                                 -> fastfingertips/list
            `fastfingertips/list/list`                            -> fastfingertips/list
            `fastfingertips/list/list/detail`                     -> fastfingertips/list

            # if a list's name is 'detail'?
            `fastfingertips/detail`                               -> fastfingertips/detail
            `fastfingertips/detail/detail`                        -> fastfingertips/detail
            `fastfingertips/list/detail`                          -> fastfingertips/detail
            `fastfingertips/list/detail/detail`                   -> fastfingertips/detail

        filters:
            `fastfingertips/list_name/decade/1990s/genre/crime+-comedy/by/popular`
            `fastfingertips/list/list_name/decade/1990s/genre/crime+-comedy/by/popular`
            `fastfingertips/list/list_name/detail/decade/1990s/genre/crime+-comedy/by/popular`

        extras:
            checks the / sign at the end and beginning of the data.
        """

        def clean_slashes(data):
            """Remove leading and trailing slashes"""
            if len(data) <= 2:
                st.error('Data is too short.')
                return None
            if data[0] == '/':
                data = data[1:]
            if data[-1] == '/':
                data = data[:-1]
            return data

        def parse_data_blocks(data):
            """Split data and extract username"""
            if '/' not in data:
                return None, None

            data_blocks = data.split('/')
            username = data_blocks[0]
            remaining_blocks = data_blocks[1:]
            return username, remaining_blocks

        def extract_list_slug(data_blocks):
            """Extract list slug from data blocks with complex logic"""
            if len(data_blocks) == 1:
                return data_blocks[0], []

            def handle_list_keyword():
                """Handle when first block is 'list'"""
                if data_blocks[1] == 'list':
                    list_slug = data_blocks[1]
                    remaining = data_blocks[2:]
                    if remaining and remaining[0] == 'detail':
                        remaining = remaining[1:]
                    return list_slug, remaining
                elif data_blocks[1] == 'detail':
                    list_slug = data_blocks[1]
                    remaining = data_blocks[2:]
                    if remaining and remaining[0] == 'detail':
                        remaining = remaining[1:]
                    return list_slug, remaining
                else:
                    list_slug = data_blocks[1]
                    remaining = data_blocks[2:]
                    if remaining and remaining[0] == 'detail':
                        remaining = remaining[1:]
                    return list_slug, remaining

            def handle_detail_keyword():
                """Handle when first block is 'detail'"""
                if data_blocks[1] == 'detail':
                    return data_blocks[0], data_blocks[2:]
                else:
                    return data_blocks[0], data_blocks[1:]

            if data_blocks[0] == 'list':
                return handle_list_keyword()
            elif data_blocks[0] == 'detail':
                return handle_detail_keyword()
            else:
                return data_blocks[0], data_blocks[1:]

        if '/' in data:
            # Clean and parse input data
            cleaned_data = clean_slashes(data)
            if not cleaned_data:
                return None

            username, data_blocks = parse_data_blocks(cleaned_data)
            if not username or not data_blocks:
                return None

            # Extract list slug using nested function
            list_slug, remaining_blocks = extract_list_slug(data_blocks)

            try:
                if all([username, list_slug]):
                    filters = ''
                    if remaining_blocks:
                        filters = '/'.join(remaining_blocks)
                    return f'{DOMAIN}/{username}/list/{list_slug}/' + filters
                else:
                    st.error('Username or list title is empty.')
            except Exception as e:
                st.error(e)
                pass
        else:
            # Username mode
            return f'{DOMAIN}/{data}/'

        return None

    @staticmethod
    def parse_letterboxd_url(url: str) -> dict:
        """Parse Letterboxd URL and extract components"""
        if '/watchlist' in url:
            pattern = r'letterboxd\.com/([^/]+)/watchlist'
            match = re.search(pattern, url)
            if match:
                return {
                    'username': match.group(1),
                    'slug': 'watchlist',
                    'type': 'watchlist'
                }
            raise ValueError(f"Invalid watchlist URL format: {url}")
        elif '/list/' in url:
            username, slug = parse_list_url(url)
            return {
                'username': username,
                'slug': slug,
                'type': 'user_list'
            }
        raise ValueError(f"Unsupported URL type: {url}")
