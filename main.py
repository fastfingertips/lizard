import streamlit as st
from letterboxdpy.constants.project import LIST_COLUMNS, WATCHLIST_COLUMNS
from letterboxdpy.core.exceptions import (
    AccessDeniedError,
    PageLoadError,
    ResourceNotFoundError,
)

from models.config import Page
from models.logger import log_step, logger
from models.manager import Input
from models.user import User
from models.userfilms import UserFilms
from models.userlist import UserList
from models.watchlist import WatchList
from widgets import display, messages, selectors
from widgets.progress import ProgressTracker


def _fetch_with_progress(collection, desc: str, total: int | None = None) -> list:
    """Fetch collection movies while rendering a real-time stqdm-style progress bar."""
    resolved_total = total if total is not None else getattr(collection, "count", None)
    with ProgressTracker(desc=desc, total=resolved_total, unit="movies") as tracker:
        return collection.fetch_movies(on_progress=tracker.update)


def watchlist_mode(
    user_instance,
    username,
    filters: str = "",
    sort_by: str | None = None,
):
    active_filters, active_sort = selectors.collection_controls(
        "watchlist",
        default_filters=filters,
        default_sort=sort_by,
        key_prefix=f"wl_{username}",
    )

    def create_watchlist(username):
        """Create WatchList instance"""
        return WatchList(
            user_instance,
            username,
            filters=active_filters,
            sort_by=active_sort,
        )

    def load_movies(watchlist):
        """Load movies from watchlist with progress bar"""
        total = 0 if watchlist.filters else None
        return _fetch_with_progress(watchlist, "Loading watchlist data...", total=total)

    def display_movies(movies, watchlist, user_instance, username):
        """Display watchlist movies or appropriate message"""
        if movies and len(movies) > 0:
            # Display movies with format from session state
            csv_format = st.session_state.get("csv_format", "Letterboxd")
            display.movies_dataframe(
                movies, columns=WATCHLIST_COLUMNS, csv_format=csv_format
            )
        elif watchlist.filters:
            messages.no_filtered_movies()
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
        display_movies(movies, watchlist, user_instance, username)
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
    """Build unified films, watchlist, and user list options dictionary"""
    is_hq_user = getattr(user_instance, "badge", None) == "HQ"
    options = {}

    films_count = getattr(user_instance, "films_count", None)
    if films_count is not None and films_count > 0:
        options[f"Films ({films_count} movies)"] = (
            f"https://letterboxd.com/{username}/films/"
        )

    if (
        not is_hq_user
        and user_instance.watchlist_length is not None
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


def _inject_collection_accents(has_films: bool, has_watchlist: bool):
    """Apply industry-standard brand accent styles to core Letterboxd collections."""
    css_rules = []
    idx = 2

    def opt_sel(n):
        return (
            f'[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-key="{n - 1}"], '
            f'[data-testid="stSelectboxVirtualDropdown"] [role="option"]:not([data-key]):nth-child({n}), '
            f'[data-testid="stSelectboxVirtualDropdown"] li:nth-child({n}), '
            f'div[data-baseweb="popover"] ul[role="listbox"] li:nth-child({n})'
        )

    if has_films:
        css_rules.append(
            f"{opt_sel(idx)} {{ "
            "border-left: 3px solid #00e054 !important; "
            "background-color: rgba(0, 224, 84, 0.08) !important; "
            "font-weight: 500 !important; }"
        )
        idx += 1

    if has_watchlist:
        css_rules.append(
            f"{opt_sel(idx)} {{ "
            "border-left: 3px solid #40bcf4 !important; "
            "background-color: rgba(64, 188, 244, 0.08) !important; "
            "font-weight: 500 !important; }"
        )
        idx += 1

    if has_films or has_watchlist:
        last = idx - 1
        css_rules.append(
            f"{opt_sel(last)} {{ "
            "border-bottom: 1px solid rgba(255, 255, 255, 0.15) !important; "
            "margin-bottom: 4px !important; }"
        )

    if css_rules:
        st.markdown(f"<style>{''.join(css_rules)}</style>", unsafe_allow_html=True)


def _load_or_cache_user(username: str):
    """Fetch user profile and list options once per session per username."""
    cache = st.session_state.get("user_cache")
    if cache and cache.get("username") == username:
        logger.info("[CACHE:HIT] user_cache username=%s", username)
        return cache["user"], cache["is_hq"], cache["options"]

    logger.info("[CACHE:MISS] user_cache username=%s", username)
    with (
        log_step("USER_PROFILE", username=username),
        st.spinner(f"Loading profile for {username}..."),
    ):
        user_instance = User(username)

    total_lists = user_instance.stats.get("lists") if user_instance.stats else None
    with (
        log_step("USER_LISTS", username=username, expected_total=total_lists),
        ProgressTracker(
            desc="Loading user lists...", total=total_lists, unit="lists"
        ) as tracker,
    ):
        user_lists = user_instance.get_lists(on_progress=tracker.update)

    with log_step("BUILD_OPTIONS", username=username):
        is_hq_user, list_options = _build_list_options(
            user_instance, user_lists, username
        )

    st.session_state["user_cache"] = {
        "username": username,
        "user": user_instance,
        "is_hq": is_hq_user,
        "options": list_options,
    }
    return user_instance, is_hq_user, list_options


def username_mode(username):
    # Early validation - fail fast
    try:
        user_instance, is_hq_user, list_options = _load_or_cache_user(username)
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
            logger.info(
                "[SELECTBOX] username=%s selected=%r url=%s",
                username,
                selected_list,
                selected_url,
            )
            if "/watchlist/" in selected_url:
                watchlist_mode(user_instance, username)
            elif "/films/" in selected_url:
                films_mode(selected_url)
            else:
                list_mode(selected_url)

    has_films = any("/films/" in url for url in list_options.values())
    has_watchlist = any("/watchlist/" in url for url in list_options.values())
    has_regular_lists = any(
        "/watchlist/" not in url and "/films/" not in url
        for url in list_options.values()
    )

    if list_options:
        _inject_collection_accents(has_films, has_watchlist)
        if has_watchlist and not has_regular_lists and not has_films:
            messages.only_watchlist(username)
        elif is_hq_user and has_regular_lists:
            messages.hq_user_status(username)
        elif not is_hq_user and has_regular_lists and not has_watchlist:
            messages.lists_no_watchlist(username)

        if getattr(user_instance, "lists_partial", False):
            messages.partial_lists_warning(
                username,
                user_instance.lists_fetched_count,
                user_instance.lists_expected_pages,
            )

        handle_list_selection(list_options)
    else:
        messages.no_public_lists(username)
        if is_hq_user:
            messages.hq_no_watchlist()
        else:
            messages.watchlist_might_be_private()


def _render_movie_collection(collection_instance, spinner_text):
    """Render details, progress bar, and dataframe for a movie collection."""
    display.object_details(collection_instance)
    try:
        total = (
            0
            if getattr(collection_instance, "filters", None)
            and isinstance(collection_instance, UserList)
            else None
        )
        movies = _fetch_with_progress(collection_instance, spinner_text, total=total)
        if (
            isinstance(collection_instance, UserFilms)
            and collection_instance.count
            and 0 < len(movies) < collection_instance.count
        ):
            messages.partial_movies_warning(len(movies), collection_instance.count)
        if not movies and getattr(collection_instance, "filters", None):
            messages.no_filtered_movies()
        else:
            csv_format = st.session_state.get("csv_format", "Letterboxd")
            display.movies_dataframe(
                movies, columns=LIST_COLUMNS, csv_format=csv_format
            )
    except Exception as e:
        messages.error(str(e))
    st.button("Get again.")


def _handle_collection_access(factory_fn, spinner_text):
    """Safely initialize and render a movie collection model."""
    try:
        collection = factory_fn()
    except ResourceNotFoundError:
        messages.list_unavailable()
        st.stop()
    except AccessDeniedError:
        messages.access_denied()
        st.stop()
    except Exception:
        messages.invalid_list_url()
        st.stop()

    _render_movie_collection(collection, spinner_text)


def list_mode(processed_input):
    url_info = Input.parse_letterboxd_url(processed_input)
    active_filters, active_sort = selectors.collection_controls(
        "list",
        default_filters=url_info.get("filters", ""),
        default_sort=url_info.get("sort_by"),
        key_prefix=f"list_{url_info['username']}_{url_info['slug']}",
    )
    _handle_collection_access(
        lambda: UserList(
            url_info["username"],
            url_info["slug"],
            filters=active_filters,
            sort_by=active_sort,
        ),
        "Loading list data...",
    )


def films_mode(processed_input):
    url_info = Input.parse_letterboxd_url(processed_input)
    active_filters, active_sort = selectors.collection_controls(
        "films",
        default_filters=url_info.get("filters", ""),
        default_sort=url_info.get("sort_by"),
        key_prefix=f"films_{url_info['username']}",
    )
    _handle_collection_access(
        lambda: UserFilms(
            url_info["username"],
            filters=active_filters,
            sort_by=active_sort,
        ),
        "Loading films data...",
    )


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

        try:
            url_info = Input.parse_letterboxd_url(processed_url)
        except Exception:
            messages.invalid_list_url()
            st.stop()

        url_type = url_info.get("type")
        if url_type == "watchlist":
            watchlist_mode(
                None,
                url_info["username"],
                filters=url_info.get("filters", ""),
                sort_by=url_info.get("sort_by"),
            )
        elif url_type == "user_films":
            films_mode(url_info.get("url", processed_url))
        elif url_type == "user":
            username_mode(url_info["username"])
        else:
            list_mode(url_info.get("url", processed_url))


if __name__ == "__main__":
    page = Page()
    page.create_title("Letterboxd List Downloader")
    page.create_footer()

    col_fmt, col_det = st.columns([3, 1], vertical_alignment="bottom")
    with col_fmt:
        st.session_state["csv_format"] = selectors.csv_format_selector()
    with col_det:
        st.session_state["show_details"] = selectors.details_toggle_selector()

    user_input = Input()
    user_input.process_data()
    determine_mode(user_input)
