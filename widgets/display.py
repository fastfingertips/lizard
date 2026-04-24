"""
Display widgets for rendering content.

These widgets display content without returning values.
"""

import pandas as pd
import streamlit as st
from letterboxdpy.constants.project import LIST_COLUMNS, CSV_FORMAT_COLUMNS


def movies_dataframe(movies_data, columns=None, csv_format="Letterboxd"):
    """
    Display movies data as a dataframe with specified columns.
    
    Args:
        movies_data: List of movie dictionaries
        columns: List of column names to display (defaults to LIST_COLUMNS)
        csv_format: CSV format name for column renaming ("Letterboxd" or "TMDB")
    """
    if columns is None:
        columns = LIST_COLUMNS
    
    # Filter and reorder data according to specified columns
    filtered_data = []
    for movie in movies_data:
        filtered_movie = {col: movie.get(col, '') for col in columns if col in movie}
        filtered_data.append(filtered_movie)
    
    # Create DataFrame with exact column order
    df = pd.DataFrame(filtered_data, columns=columns)
    
    # Rename columns based on selected format
    column_mapping = CSV_FORMAT_COLUMNS.get(csv_format, CSV_FORMAT_COLUMNS["Letterboxd"])
    df = df.rename(columns=column_mapping)
    
    st.dataframe(
        df,
        hide_index=True,
        width="stretch",
    )


def object_details(obj, title=None):
    """
    Display object details using metadata property if available.

    Args:
        obj: Object to display
        title: Optional title for the section
    """
    if title:
        st.subheader(title)

    # Try to use metadata property first
    if hasattr(obj, 'metadata'):
        details = obj.metadata
    else:
        # Fallback to __dict__ attributes
        details = {}
        for key, value in obj.__dict__.items():
            if 'dom' not in key.lower() and not key.startswith('_'):
                details[key] = value

    with st.expander(title or "Details", expanded=False):
        st.json(details, expanded=True)
