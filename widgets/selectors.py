"""
Selector widgets that return values.

These widgets get user input and return the selected value.
"""

import re

import streamlit as st
from letterboxdpy.constants.project import CSV_FORMAT_COLUMNS, GENRES


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


def details_toggle_selector() -> bool:
    """Display toggle widget to control whether metadata Details expanders render."""
    url_details = st.query_params.get("details", "").lower() in (
        "1",
        "true",
        "yes",
    )
    return st.toggle(
        "Show Details",
        value=url_details,
        help="Display raw JSON metadata for loaded profiles and collections",
    )


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


def _select_from_map(
    label: str,
    option_map: dict[str, str | None],
    default_val: str | None,
    key: str,
) -> str | None:
    """Render a selectbox backed by a label->slug dictionary."""
    choices = dict(option_map)
    if default_val and default_val not in choices.values():
        choices[f"Custom ({default_val})"] = default_val

    labels = list(choices.keys())
    default_idx = next(
        (i for i, lbl in enumerate(labels) if choices[lbl] == default_val),
        0,
    )
    selected = st.selectbox(label, options=labels, index=default_idx, key=key)
    return choices[selected]


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
    return _select_from_map("Sort by", sort_map, default_sort, f"{key_prefix}_sort")


GENRE_LABELS: dict[str, str] = {
    "science-fiction": "Science Fiction",
    "tv-movie": "TV Movie",
}

GENRE_OPTIONS: dict[str, str | None] = {
    "All Genres": None,
    **{GENRE_LABELS.get(g, g.title()): g for g in GENRES},
}

DECADE_OPTIONS: dict[str, str | None] = {
    "All Decades": None,
    **{f"{d}s": f"{d}s" for d in range(2020, 1860, -10)},
}

RATING_OPTIONS: dict[str, str | None] = {
    "All Ratings": None,
    "5.0": "5",
    "4.5": "4.5",
    "4.0": "4",
    "3.5": "3.5",
    "3.0": "3",
    "2.5": "2.5",
    "2.0": "2",
    "1.5": "1.5",
    "1.0": "1",
    "0.5": "0.5",
    "Unrated": "none",
}


def _parse_filter_path(filters: str) -> dict[str, str | None]:
    """Extract rated, decade, genre, and remaining path segments from filter string."""
    clean = (filters or "").strip("/")
    parsed: dict[str, str | None] = {
        "rated": None,
        "decade": None,
        "genre": None,
        "extra": None,
    }
    if not clean:
        return parsed

    for key in ("rated", "decade", "genre"):
        match = re.search(rf"(?:^|/){key}/([^/]+)", clean)
        if match:
            val = match.group(1)
            if key == "rated" and val.endswith(".0"):
                val = val[:-2]
            parsed[key] = val
            clean = re.sub(rf"(?:^|/){key}/[^/]+", "", clean).strip("/")

    parsed["extra"] = clean or None
    return parsed


def collection_controls(
    collection_type: str = "list",
    default_filters: str = "",
    default_sort: str | None = None,
    key_prefix: str = "collection",
) -> tuple[str, str | None]:
    """Render Letterboxd sort and filter selectors and return (filters, sort_by)."""
    parsed = _parse_filter_path(default_filters)
    cols = st.columns(4 if collection_type == "films" else 3)

    with cols[0]:
        active_sort = sort_selector(collection_type, default_sort, key_prefix)
    with cols[1]:
        genre = _select_from_map(
            "Genre", GENRE_OPTIONS, parsed["genre"], f"{key_prefix}_genre"
        )
    with cols[2]:
        decade = _select_from_map(
            "Decade", DECADE_OPTIONS, parsed["decade"], f"{key_prefix}_decade"
        )

    rated = None
    if collection_type == "films":
        with cols[3]:
            rated = _select_from_map(
                "Rating", RATING_OPTIONS, parsed["rated"], f"{key_prefix}_rated"
            )

    segments = []
    if rated:
        segments.append(f"rated/{rated}")
    if decade:
        segments.append(f"decade/{decade}")
    if genre:
        segments.append(f"genre/{genre}")
    if parsed["extra"]:
        segments.append(parsed["extra"])

    return "/".join(segments), active_sort
