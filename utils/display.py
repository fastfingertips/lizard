import pandas as pd
import streamlit as st
from constants import LIST_COLUMNS


def display_movies_dataframe(movies_data, columns=None):
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


def display_object_details(obj, title=None):
    """
    Display object details with sensitive data filtered out.

    Args:
        obj: Object to display
        title: Optional title for the section
    """
    if title:
        st.subheader(title)

    # Filter out sensitive attributes
    details = {}
    for key, value in obj.__dict__.items():
        if 'dom' not in key.lower() and not key.startswith('_'):
            details[key] = value

    st.json(details, expanded=False)
