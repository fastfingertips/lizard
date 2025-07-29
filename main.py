import streamlit as st
from letterboxdpy.core.scraper import parse_url
from letterboxdpy.user import User
from letterboxdpy.utils.utils_parser import is_list
from letterboxdpy.pages.user_list import extract_list_meta
from models.config import Page
from models.manager import Input
from models.watchlist import WatchList
from models.userlist import UserList
from models.url import Url
from constants import WATCHLIST_COLUMNS, LIST_COLUMNS
from utils import display, messages


def watchlist_mode(user_instance, username):

    def create_watchlist(username):
        """Create WatchList instance"""
        watchlist_url = f"https://letterboxd.com/{username}/watchlist/"
        url_obj = Url(watchlist_url)
        return WatchList(url_obj, username)

    def load_movies(watchlist):
        """Load movies from watchlist with spinner"""
        with st.spinner('Loading watchlist data...'):
            return watchlist.movies

    def display_movies(movies, user_instance, username):
        """Display watchlist movies or appropriate message"""
        if movies and len(movies) > 0:
            # Display movies
            display.movies_dataframe(movies, columns=WATCHLIST_COLUMNS)
        else:
            if hasattr(user_instance, 'watchlist_length') and user_instance.watchlist_length == 0:
                messages.watchlist_empty(username)
            else:
                messages.watchlist_private(username)

    def handle_error(error):
        """Handle watchlist loading errors"""
        messages.error(str(error))

    try:
        watchlist = create_watchlist(username)
        # Display watchlist details first, before loading movies
        display.object_details(watchlist)
        
        # Then load and display movies
        movies = load_movies(watchlist)
        display_movies(movies, user_instance, username)
    except Exception as e:
        handle_error(e)

def username_mode(username):
    # Early validation - fail fast
    try:
        user_instance = User(username)
        user_lists = user_instance.get_lists()
        display.object_details(user_instance)
    except Exception:
        messages.user_not_found(username)
        st.stop()

    # Nested functions after validation
    def get_watchlist(is_hq_user, user_instance, username):
        """Get watchlist options if available"""
        if not is_hq_user and user_instance.watchlist_length and user_instance.watchlist_length > 0:
            watchlist_url = f"https://letterboxd.com/{username}/watchlist/"
            return {f"Watchlist ({user_instance.watchlist_length} movies)": watchlist_url}
        return {}

    def get_lists(user_lists):
        """Get regular list options if available"""
        options = {}
        if user_lists and 'lists' in user_lists and user_lists['lists']:
            for _, list_data in user_lists['lists'].items():
                display_name = f"{list_data['title']} ({list_data['count']} movies)"
                options[display_name] = list_data['url']
        return options

    def has_watchlist(watchlist_options):
        """Check if watchlist is available"""
        return len(watchlist_options) > 0

    def has_lists(regular_list_options):
        """Check if regular lists are available"""
        return len(regular_list_options) > 0

    def handle_list_selection(list_options, user_instance, username):
        """Handle list selection and navigation"""
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

    is_hq_user = user_instance.is_hq
    watchlist_options = get_watchlist(is_hq_user, user_instance, username)
    regular_list_options = get_lists(user_lists)
    has_watchlist_flag = has_watchlist(watchlist_options)
    has_regular_lists_flag = has_lists(regular_list_options)
    list_options = {**watchlist_options, **regular_list_options}

    if list_options:
        if has_watchlist_flag and not has_regular_lists_flag:
            messages.only_watchlist(username)
        elif is_hq_user and has_regular_lists_flag:
            messages.hq_user_status(username)
        elif not is_hq_user and has_regular_lists_flag and not has_watchlist_flag:
            messages.lists_no_watchlist(username)

        handle_list_selection(list_options, user_instance, username)
    else:
        messages.no_public_lists(username)
        if is_hq_user:
            messages.hq_no_watchlist()
        else:
            messages.watchlist_might_be_private()

def list_mode(processed_input):
    # Early validation - fail fast
    url_dom = parse_url(processed_input)
    is_list_result = is_list(url_dom)

    if not is_list_result:
        messages.invalid_list_url()
        st.stop()

    # Nested functions after validation
    def create_list(url_dom, processed_input):
        """Create UserList instance from validated URL"""
        list_meta = extract_list_meta(url_dom, processed_input)
        url_info = Input.parse_letterboxd_url(list_meta['url'])

        user_list = UserList(
            Url(list_meta['url'], url_dom),
            url_info['username'],
            url_info['slug']
        )

        return user_list, list_meta

    def display_content(user_list, list_meta):
        """Display list details and movies if available"""
        display.object_details(user_list)

        if list_meta['is_available']:
            display.movies_dataframe(user_list.movies, columns=LIST_COLUMNS)
        else:
            messages.list_unavailable()

    st.button('Get again.')
    user_list, list_meta = create_list(url_dom, processed_input)
    display_content(user_list, list_meta)

def determine_mode(user_input):
    """Determine which mode to use based on user input"""
    if not user_input.data:
        messages.awaiting_input()
        st.stop()

    if user_input.is_username:
        username_mode(user_input.data)
        st.stop()
    else:
        try:
            if user_input.is_url:
                processed_url = user_input.data
            else:
                processed_url = user_input.convert_to_url(user_input.data)

            if not processed_url:
                messages.invalid_input()
                st.stop()

            list_mode(processed_url)
        except Exception:
            messages.invalid_input()
            st.stop()


if __name__ == "__main__":
    page = Page()
    page.create_title()
    page.create_footer()
    user_input = Input()
    user_input.process_data()
    determine_mode(user_input)