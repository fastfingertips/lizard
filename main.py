import pandas as pd
import streamlit as st
from letterboxdpy.core.scraper import parse_url

from models.checker import Checker
from models.config import Page
from models.manager import Input
from models.movie_list import MovieList
from models.notifier import Notifier
from models.parser.utils import catch_error_message
from models.url import Url
from models.url.helpers import convert_to_pattern

def list_mode(processed_input):
    
    url_dom = parse_url(processed_input)
    err_msg = catch_error_message(url_dom)

    checker = Checker(url_dom)
    is_list = checker.is_list()

    if err_msg:
        st.error(f'{err_msg}', icon='👀')
        if not is_list:
            st.warning(f'The address is not a Letterboxd list.', icon='💡')
            st.warning('Please enter a valid **list url** or **username/list-title.**', icon='💡')
        st.stop()

    button = st.button('Get again.')

    # Notifier
    notifier = Notifier()
    notifier.set_link_code("fastfingertips-lizard")
    notifier.send(f'List verified: {processed_input}')

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

    notifier.send(f'List parsing: {processed_input}')
    if list_meta['is_available']:
        st.dataframe(
            pd.DataFrame(
                movie_list.movies,
                columns=["Rank", "Year", "Title", "LetterboxdURI"]
            ),
            hide_index=True,
            use_container_width=True,
        )
        notifier.send(f'List parsed: {processed_input}')
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
        processed_input = user_input.data
        processed_input = user_input.convert_to_url(processed_input)
    else:
        if user_input.is_short_url:
            processed_input = user_input.data.replace('/detail', '')
        else:
            processed_input = convert_to_pattern(user_input.data)
            processed_input = user_input.convert_to_url(processed_input)
        list_mode(processed_input)

    if not processed_input:
        st.warning('**username/list-title.**', icon='💡')
        st.stop()