"""
Selector widgets that return values.

These widgets get user input and return the selected value.
"""

import streamlit as st
from letterboxdpy.constants.project import CSV_FORMAT_COLUMNS


def csv_format_selector():
    """
    Display CSV format selection widget and return selected format.

    Returns:
        str: Selected format name ("Letterboxd" or "TMDB")
    """
    # Get format from URL query parameter if present
    query_params = st.query_params
    url_format = query_params.get("format", "").lower()

    # Map URL parameter to format name
    format_options = list(CSV_FORMAT_COLUMNS.keys())
    format_map = {f.lower(): f for f in format_options}

    # Determine default based on URL param or default to first option
    if url_format in format_map:
        default_format = format_map[url_format]
    else:
        default_format = format_options[0]  # Default: Letterboxd

    # CSV format selection - compact horizontal radio
    csv_format = st.radio(
        "CSV Format",
        options=format_options,
        index=format_options.index(default_format),
        horizontal=True,
        help="Select export format for CSV download",
    )

    return csv_format


COMMON_SORT_OPTIONS: dict[str, str | None] = {
    "Default": None,
    "Popularity": "popular",
    "Highest Rating": "rating",
    "Lowest Rating": "rating-lowest",
    "Newest Release": "release",
    "Earliest Release": "release-earliest",
    "Title (A-Z)": "name",
    "Shortest Runtime": "shortest",
    "Longest Runtime": "longest",
    "Shuffle": "shuffle",
}

COLLECTION_SORT_EXTRAS: dict[str, dict[str, str]] = {
    "list": {
        "Reverse Order": "reverse",
        "Recently Added": "added",
        "Earliest Added": "added-earliest",
    },
    "watchlist": {
        "Earliest Added": "date-earliest",
    },
    "films": {
        "Member Rating (High-Low)": "entry-rating",
        "Member Rating (Low-High)": "entry-rating-lowest",
        "Recently Logged": "date",
        "Earliest Logged": "date-earliest",
    },
}


def sort_selector(
    collection_type: str = "list",
    default_sort: str | None = None,
    key_prefix: str = "collection",
) -> str | None:
    """Render Letterboxd sort order selector and return canonical sort_by slug."""
    sort_map: dict[str, str | None] = {
        **COMMON_SORT_OPTIONS,
        **COLLECTION_SORT_EXTRAS.get(collection_type, {}),
    }
    if default_sort and default_sort not in sort_map.values():
        sort_map[f"Custom ({default_sort})"] = default_sort

    labels = list(sort_map.keys())
    default_idx = next(
        (i for i, lbl in enumerate(labels) if sort_map[lbl] == default_sort),
        0,
    )
    selected = st.selectbox(
        "Sort by",
        options=labels,
        index=default_idx,
        key=f"{key_prefix}_sort",
    )
    return sort_map[selected]
