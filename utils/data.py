from constants import LETTERBOXD_COLUMNS


def create_movie_data(**kwargs):
    """
    Create movie data dictionary following Letterboxd import format.
    
    Supports all official Letterboxd CSV import fields:
    https://letterboxd.com/about/importing-data/
    
    Args:
        **kwargs: Movie data fields (letterboxd_uri, title, year, rating, etc.)
        
    Returns:
        dict: Filtered movie data with Letterboxd column names
    """
    
    def _is_valid_value(value):
        """Check if value is valid for Letterboxd import."""
        return value and isinstance(value, (str, int, bool))
    
    # Filter and map valid fields only
    movie_data = {}
    for field_name, value in kwargs.items():
        if field_name in LETTERBOXD_COLUMNS and _is_valid_value(value):
            column_name = LETTERBOXD_COLUMNS[field_name]
            movie_data[column_name] = value
            
    return movie_data
