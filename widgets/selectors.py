"""
Selector widgets that return values.

These widgets get user input and return the selected value.
"""

import streamlit as st
from constants import CSV_FORMAT_COLUMNS


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
        help="Select export format for CSV download"
    )
    
    return csv_format
