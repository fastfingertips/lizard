import pandas as pd
import streamlit as st
from letterboxdpy.core.scraper import parse_url
from letterboxdpy.user import User

from models.checker import Checker
from models.config import Page
from models.manager import Input
from models.movie_list import MovieList
from models.notifier import Notifier
from models.parser.utils import catch_error_message
from models.url import Url
from models.url.helpers import convert_to_pattern

def username_mode(username):
    """Handle username input - show user's lists and allow selection"""
    try:
        user_instance = User(username)
        user_lists = user_instance.get_lists()
    except Exception:
        st.error(f"User '{username}' not found.")
        st.stop()

    # Display user lists
    if user_lists and 'lists' in user_lists and user_lists['lists']:
        st.success(f"Found {user_lists['count']} lists for **{username}**")

        # Create list options for selectbox
        list_options = {}
        for _, list_data in user_lists['lists'].items():
            display_name = f"{list_data['title']} ({list_data['count']} movies)"
            list_options[display_name] = list_data['url']

        selected_list = st.selectbox(
            "Select a list:",
            options=["Choose a list..."] + list(list_options.keys()),
            index=0
        )

        # Show selected list details and movies
        if selected_list and selected_list != "Choose a list...":
            selected_url = list_options[selected_list]

            # Find selected list data
            selected_list_data = None
            for list_data in user_lists['lists'].values():
                if list_data['url'] == selected_url:
                    selected_list_data = list_data
                    break

            if selected_list_data:
                # Show compact list details in one line
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Movies", selected_list_data['count'])
                with col2:
                    st.metric("Likes", selected_list_data['likes'])
                with col3:
                    st.metric("Comments", selected_list_data['comments'])

                # Show description if available (compact)
                if selected_list_data.get('description'):
                    with st.expander("Description"):
                        st.write(selected_list_data['description'])

            # Show movies directly below
            list_mode(selected_url)
    else:
        st.write(f"User '{username}' has no lists.")


def list_mode(processed_input):

    url_dom = parse_url(processed_input)
    err_msg = catch_error_message(url_dom)

    checker = Checker(url_dom)
    is_list = checker.is_list()

    if err_msg:
        st.error(f'{err_msg}', icon='👀')
        if not is_list:
            st.warning(f'The address is not a Letterboxd list.', icon='💡')
            st.warning('Please enter a valid **username**, **list url** or **username/list-title.**', icon='💡')
        st.stop()

    button = st.button('Get again.')

    # create checker object for list
    list_meta = checker.get_list_meta(processed_input)

    # address is list, so we can create the object now
    movie_list = MovieList(
        Url(
            list_meta['url'],
            url_dom
        )
    )

    list_details = {}
    for key, value in movie_list.__dict__.items():
        list_details[key] = '🚫' if 'dom' in key else value
    json_info = st.json(list_details, expanded=False)
    # since this process may take a long time, we print the list information
    # ... on the screen before. this way we can see which list is downloaded.

    if list_meta['is_available']:
        st.dataframe(
            pd.DataFrame(
                movie_list.movies,
                columns=["Rank", "Year", "Title", "LetterboxdURI"]
            ),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.warning('List is not available.')


if __name__ == "__main__":
    page = Page()
    page.create_title()
    page.create_footer()
    user_input = Input()
    user_input.process_data()
 
    if not user_input.data:
        st.write('_Awaiting input.._')
        st.stop()

    if user_input.is_username:
        username_mode(user_input.data)
        st.stop()
    else:
        if user_input.is_short_url:
            processed_input = user_input.data.replace('/detail', '')
        else:
            processed_input = convert_to_pattern(user_input.data)
            processed_input = user_input.convert_to_url(processed_input)
        list_mode(processed_input)

    if not processed_input:
        st.warning('Please enter a valid **username**, **list url** or **username/list-title.**', icon='💡')
        st.stop()