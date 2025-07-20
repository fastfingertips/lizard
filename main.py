import streamlit as st
from letterboxdpy.core.scraper import parse_url
from letterboxdpy.user import User
from letterboxdpy.utils.utils_parser import is_list
from letterboxdpy.pages.user_list import extract_list_meta
from models.config import Page
from models.manager import Input
from models.movie_list import MovieList
from utils.parser import catch_error_message
from models.url import Url
from constants import WATCHLIST_COLUMNS, LIST_COLUMNS
from utils.display import display_movies_dataframe, display_object_details
from utils.data import create_movie_data


def watchlist_mode(user_instance, username):
    try:
        with st.spinner('Loading watchlist data...'):
            watchlist_movies = user_instance.get_watchlist_movies()

        if watchlist_movies:
            movies_data = []
            for rank, (_, movie_info) in enumerate(watchlist_movies.items(), 1):
                movie_data = create_movie_data(
                    rank=rank,
                    title=movie_info.get('name', ''),
                    letterboxd_uri=movie_info.get('url', f"https://letterboxd.com/film/{movie_info.get('slug', '')}/")
                )
                movies_data.append(movie_data)

            display_movies_dataframe(movies_data, columns=WATCHLIST_COLUMNS)
        else:
            if hasattr(user_instance, 'watchlist_length') and user_instance.watchlist_length == 0:
                st.info(f"**{username}**'s watchlist is empty.")
            else:
                st.info(f"**{username}**'s watchlist is not accessible or private.")

    except Exception as e:
        st.error(f"Error loading watchlist: {str(e)}")


def username_mode(username):
    try:
        user_instance = User(username)
        user_lists = user_instance.get_lists()

        # Display user instance data
        display_object_details(user_instance, "User Details")

    except Exception:
        st.error(f"User '[{username}](https://letterboxd.com/{username}/)' not found.")
        st.stop()

    list_options = {}
    has_watchlist = False
    has_regular_lists = False
    is_hq_user = user_instance.is_hq

    if not is_hq_user and user_instance.watchlist_length and user_instance.watchlist_length > 0:
        watchlist_url = f"https://letterboxd.com/{username}/watchlist/"
        list_options[f"Watchlist ({user_instance.watchlist_length} movies)"] = watchlist_url
        has_watchlist = True

    if user_lists and 'lists' in user_lists and user_lists['lists']:
        for _, list_data in user_lists['lists'].items():
            display_name = f"{list_data['title']} ({list_data['count']} movies)"
            list_options[display_name] = list_data['url']
            has_regular_lists = True

    if list_options:
        if has_watchlist and not has_regular_lists:
            st.info(f"**[{username}](https://letterboxd.com/{username}/)** has only a watchlist (no public lists).")
        elif is_hq_user and has_regular_lists:
            st.info(f"**[{username}](https://letterboxd.com/{username}/)** is an HQ user (no watchlist available).")
        elif not is_hq_user and has_regular_lists and not has_watchlist:
            st.info(f"**[{username}](https://letterboxd.com/{username}/)** has public lists. Watchlist might be private or empty.")

        selected_list = st.selectbox(
            "Select a list:",
            options=["Choose a list..."] + list(list_options.keys()),
            index=0
        )

        if selected_list and selected_list != "Choose a list...":
            selected_url = list_options[selected_list]
            if '/watchlist/' in selected_url:
                watchlist_mode(user_instance, username)
            else:
                list_mode(selected_url)
    else:
        st.info(f"**[{username}](https://letterboxd.com/{username}/)** has no public lists.")
        if is_hq_user:
            st.info("HQ users do not have watchlists.")
        else:
            st.info("The user's watchlist might be private or empty.")


def list_mode(processed_input):

    url_dom = parse_url(processed_input)
    err_msg = catch_error_message(url_dom)

    is_list_result = is_list(url_dom)

    if err_msg:
        st.error(f'{err_msg}', icon='👀')
        if not is_list:
            st.warning('The address is not a Letterboxd list.', icon='💡')
            st.warning('Please enter a valid **username**, **list url** or **username/list-title.**', icon='💡')
        st.stop()

    st.button('Get again.')

    list_meta = extract_list_meta(url_dom, processed_input)
    movie_list = MovieList(
        Url(
            list_meta['url'],
            url_dom
        )
    )

    # Display list instance data
    display_object_details(movie_list, "List Details")

    if list_meta['is_available']:
        display_movies_dataframe(movie_list.movies, columns=LIST_COLUMNS)
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
            processed_input = Url.convert_to_pattern(user_input.data)
            processed_input = user_input.convert_to_url(processed_input)
        list_mode(processed_input)

    if not processed_input:
        st.warning('Please enter a valid **username**, **list url** or **username/list-title.**', icon='💡')
        st.stop()