import streamlit as st
from letterboxdpy.constants.project import LIST_COLUMNS, WATCHLIST_COLUMNS
from letterboxdpy.core.exceptions import (
    AccessDeniedError,
    PageLoadError,
    ResourceNotFoundError,
)

from models.config import Page
from models.manager import Input
from models.user import User
from models.userlist import UserList
from models.watchlist import WatchList
from widgets import display, messages, selectors


def watchlist_mode(user_instance, username):

    def create_watchlist(username):
        """Create WatchList instance"""
        return WatchList(username)

    def load_movies(watchlist):
        """Load movies from watchlist with spinner"""
        with st.spinner("Loading watchlist data..."):
            return watchlist.movies

    def display_movies(movies, user_instance, username):
        """Display watchlist movies or appropriate message"""
        if movies and len(movies) > 0:
            # Display movies with format from session state
            csv_format = st.session_state.get("csv_format", "Letterboxd")
            display.movies_dataframe(
                movies, columns=WATCHLIST_COLUMNS, csv_format=csv_format
            )
        else:
            if (
                hasattr(user_instance, "watchlist_length")
                and user_instance.watchlist_length == 0
            ):
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


def _handle_access_denied(username):
    messages.access_denied(username)
    st.info(
        f"You can still access **[{username}](https://letterboxd.com/{username}/)**'s "
        "watchlist or specific list directly:"
    )
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Load Watchlist", type="primary"):
            watchlist_mode(None, username)
            st.stop()
    with col2:
        st.caption(f"Example: `{username}/list-slug/` or `{username}/watchlist/`")
    st.stop()


def _build_list_options(user_instance, user_lists, username):
    """Build unified watchlist and user list options dictionary"""
    is_hq_user = getattr(user_instance, "badge", None) == "HQ"
    options = {}

    if (
        not is_hq_user
        and user_instance.watchlist_length
        and user_instance.watchlist_length > 0
    ):
        options[f"Watchlist ({user_instance.watchlist_length} movies)"] = (
            f"https://letterboxd.com/{username}/watchlist/"
        )

    if user_lists and "lists" in user_lists and user_lists["lists"]:
        for list_data in user_lists["lists"].values():
            options[f"{list_data['title']} ({list_data['count']} movies)"] = list_data[
                "url"
            ]

    return is_hq_user, options


def username_mode(username):
    # Early validation - fail fast
    try:
        user_instance = User(username)
        user_lists = user_instance.get_lists()
        display.object_details(user_instance)
    except ResourceNotFoundError:
        messages.user_not_found(username)
        st.stop()
    except AccessDeniedError:
        _handle_access_denied(username)
    except PageLoadError as exc:
        messages.network_error(str(exc))
        st.stop()
    except Exception as exc:
        messages.error(str(exc))
        st.stop()

    def handle_list_selection(list_options):
        selected_list = st.selectbox(
            "Select a list:",
            options=["Choose a list...", *list(list_options.keys())],
            index=0,
        )

        if selected_list and selected_list != "Choose a list...":
            selected_url = list_options[selected_list]
            if "/watchlist/" in selected_url:
                watchlist_mode(user_instance, username)
            else:
                list_mode(selected_url)

    is_hq_user, list_options = _build_list_options(user_instance, user_lists, username)
    has_watchlist = any("/watchlist/" in url for url in list_options.values())
    has_regular_lists = any("/watchlist/" not in url for url in list_options.values())

    if list_options:
        if has_watchlist and not has_regular_lists:
            messages.only_watchlist(username)
        elif is_hq_user and has_regular_lists:
            messages.hq_user_status(username)
        elif not is_hq_user and has_regular_lists and not has_watchlist:
            messages.lists_no_watchlist(username)

        handle_list_selection(list_options)
    else:
        messages.no_public_lists(username)
        if is_hq_user:
            messages.hq_no_watchlist()
        else:
            messages.watchlist_might_be_private()


def list_mode(processed_input):
    try:
        url_info = Input.parse_letterboxd_url(processed_input)
        user_list = UserList(url_info["username"], url_info["slug"])
    except ResourceNotFoundError:
        messages.list_unavailable()
        st.stop()
    except AccessDeniedError:
        messages.access_denied()
        st.stop()
    except Exception:
        messages.invalid_list_url()
        st.stop()

    def load_movies(user_list):
        """Load movies from user list with spinner."""
        with st.spinner("Loading list data..."):
            return user_list.movies

    def display_content(user_list):
        """Display list details and movies if available"""
        display.object_details(user_list)

        try:
            movies = load_movies(user_list)
            csv_format = st.session_state.get("csv_format", "Letterboxd")
            display.movies_dataframe(
                movies, columns=LIST_COLUMNS, csv_format=csv_format
            )
        except Exception as e:
            messages.error(str(e))

    display_content(user_list)
    st.button("Get again.")


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
                processed_url = user_input.data.rstrip("/") + "/"
            else:
                processed_url = user_input.convert_to_url(user_input.data)
        except Exception:
            messages.invalid_input()
            st.stop()

        if not processed_url:
            messages.invalid_input()
            st.stop()

        if "/watchlist/" in processed_url or processed_url.endswith("/watchlist/"):
            url_info = Input.parse_letterboxd_url(processed_url)
            watchlist_mode(None, url_info["username"])
        else:
            url_info = Input.parse_letterboxd_url(processed_url)
            if url_info.get("type") == "user":
                username_mode(url_info["username"])
            else:
                list_mode(processed_url)


if __name__ == "__main__":
    page = Page()
    page.create_title("Letterboxd List Downloader")
    page.create_footer()

    csv_format = selectors.csv_format_selector()
    st.session_state["csv_format"] = csv_format

    user_input = Input()
    user_input.process_data()
    determine_mode(user_input)
