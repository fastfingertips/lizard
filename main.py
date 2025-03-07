from models.config import Page
from models.manager import Input
from models.checker import Checker
from models.movie_list import MovieList
from models.notifier import Notifier
import streamlit as st
import pandas as pd

from models.url import (
    convert_to_pattern,
    is_short_url,
    is_url,
    Url
    )

from models.utils import (
    get_dom_from_url,
    get_csv_syntax
    )

def catch_error_message(url_dom) -> bool|str:
    err = url_dom.find('body', class_='error')
    if err:
        err = url_dom.find('section', class_='message').p.get_text()
        err = err.split('\n')[0].strip()
        return err
    return False

if __name__ == "__main__":

    # Render
    page = Page()
    page.create_title()
    page.create_footer()
    print('Page initialized.')

    # Input
    input_manager = Input()
    data = input_manager.process_data()
    user_input_data = data['user_input_data']
    user_input_type = data['user_input_type']
    print('Input initialized.')

    # Process data
    if not user_input_data:
        st.write('_Awaiting input.._')
        st.stop()
    
    input_is_url = is_url(user_input_data)
    url_is_short = is_short_url(user_input_data)

    if url_is_short:
        user_input = user_input_data.replace('/detail', '')
    else:
        user_input = convert_to_pattern(user_input_data)
        user_input = input_manager.convert_to_url(user_input)

    if not user_input:
        st.warning('**username/list-title.**', icon='💡')
    else:
        # create checker object for page
        url_dom = get_dom_from_url(user_input)
        err_msg = catch_error_message(url_dom)

        checker = Checker(url_dom)
        list_meta_verify = checker.check_page_is_list()

        if err_msg:
            st.error(f'{err_msg}', icon='👀')
        if list_meta_verify['is_list']:
            button = st.button('Get again.')

            # Notifier
            notifier = Notifier()
            notifier.set_link_code("fastfingertips-lizard")
            notifier.send(f'List verified: {user_input}')

            # create checker object for list
            checked_list = checker.user_list_check(user_input)

            # address is list, so we can create the object now
            movie_list = MovieList(
                Url(
                    checked_list['list_url'],
                    url_dom
                )
            )

            list_details = {}
            for key, value in movie_list.__dict__.items():
                list_details[key] = '🚫' if 'dom' in key else value
            json_info = st.json(list_details, expanded=False)
            # since this process may take a long time, we print the list information
            # ... on the screen before. this way we can see which list is downloaded.

            notifier.send(f'List parsing: {user_input}')
            if checked_list['list_avaliable']:
                st.dataframe(
                    pd.DataFrame(
                        movie_list.movies,
                        columns=["Rank", "Year", "Title", "LetterboxdURI"]
                    ),
                    hide_index=True,
                    use_container_width=True,
                )
                notifier.send(f'List parsed: {user_input}')

                if False:
                    # Download process
                    csv_data = get_csv_syntax(movie_list.movies)
                    download_filename = movie_list.slug + '.csv'

                    download_button = st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=download_filename,
                        mime='text/csv'
                    )

                    if download_button:
                        st.success(f'{download_filename} downloaded.')
                        notifier.send(f'List downlaoded: {user_input}')
        else:
            st.warning('Please enter a valid **list url** or **username/list-title.**', icon='💡')