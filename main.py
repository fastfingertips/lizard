from models.config import Page
from models.manager import Input
from models.checker import Checker
from models.movie_list import MovieList
from models.notifier import Notifier
import streamlit as st
import pandas as pd

from models.url import (
    convert_to_pattern,
    Url
    )

from models.utils import (
    get_dom_from_url,
    get_csv_syntax,
    catch_error_message
    )

if __name__ == "__main__":

    # Render
    page = Page()
    page.create_title()
    page.create_footer()

    # Input
    user_input = Input()
    user_input.process_data()

    if not user_input.data:
        st.write('_Awaiting input.._')
        st.stop()

    if user_input.is_short_url:
        processed_input = user_input.data.replace('/detail', '')
    else:
        processed_input = convert_to_pattern(user_input.data)
        processed_input = user_input.convert_to_url(processed_input)

    if not processed_input:
        st.warning('**username/list-title.**', icon='💡')
    else:
        # create checker object for page
        url_dom = get_dom_from_url(processed_input)
        err_msg = catch_error_message(url_dom)

        checker = Checker(url_dom)
        is_list = checker.is_list()

        if err_msg:
            st.error(f'{err_msg}', icon='👀')
        if is_list:
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
                        notifier.send(f'List downlaoded: {processed_input}')
        else:
            st.warning('Please enter a valid **list url** or **username/list-title.**', icon='💡')
