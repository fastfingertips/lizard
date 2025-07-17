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
