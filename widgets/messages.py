"""
Message widgets for displaying notifications.

These widgets display status messages, warnings, and errors.
"""

import streamlit as st


def user_not_found(username):
    """Display user not found error message"""
    st.error(f"User '[{username}](https://letterboxd.com/{username}/)' not found.")


def invalid_list_url():
    """Display invalid list URL warning"""
    st.warning('The address is not a Letterboxd list.', icon='💡')
    st.warning('Please enter a valid **username**, **list url** or **username/list-title.**', icon='💡')


def invalid_input():
    """Display invalid input warning"""
    st.warning('Please enter a valid **username**, **list url** or **username/list-title.**', icon='💡')


def watchlist_empty(username):
    """Display watchlist empty message"""
    st.info(f"**{username}**'s watchlist is empty.")


def watchlist_private(username):
    """Display watchlist private/inaccessible message"""
    st.info(f"**{username}**'s watchlist is not accessible or private.")


def only_watchlist(username):
    """Display only watchlist available message"""
    st.info(f"**[{username}](https://letterboxd.com/{username}/)** has only a watchlist (no public lists).")


def hq_user_status(username):
    """Display HQ user status message"""
    st.info(f"**[{username}](https://letterboxd.com/{username}/)** is an HQ user (no watchlist available).")


def lists_no_watchlist(username):
    """Display lists available but no watchlist message"""
    st.info(f"**[{username}](https://letterboxd.com/{username}/)** has public lists. Watchlist might be private or empty.")


def no_public_lists(username):
    """Display no public lists message"""
    st.info(f"**[{username}](https://letterboxd.com/{username}/)** has no public lists.")


def hq_no_watchlist():
    """Display HQ users don't have watchlists message"""
    st.info("HQ users do not have watchlists.")


def watchlist_might_be_private():
    """Display watchlist might be private message"""
    st.info("The user's watchlist might be private or empty.")


def list_unavailable():
    """Display list unavailable warning"""
    st.warning('List is not available.')


def error(message):
    """Display generic error message"""
    st.error(f"Error: {message}")


def awaiting_input():
    """Display awaiting input message"""
    st.write('_Awaiting input.._')
