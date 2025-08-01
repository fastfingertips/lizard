import pandas as pd
import streamlit as st
from constants import LIST_COLUMNS


def movies_dataframe(movies_data, columns=None):
    """
    Display movies data as a dataframe with specified columns.
    
    Args:
        movies_data: List of movie dictionaries
        columns: List of column names to display (defaults to LIST_COLUMNS)
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
    
    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
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

    st.json(details, expanded=False)
