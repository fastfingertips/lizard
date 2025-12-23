# Column definitions for different data types
LIST_COLUMNS = ['Rank', 'Title', 'LetterboxdURI']
WATCHLIST_COLUMNS = ['Rank', 'Title', 'LetterboxdURI']

# Letterboxd official import format column mappings
# https://letterboxd.com/about/importing-data/
LETTERBOXD_COLUMNS = {
    'letterboxd_uri': 'LetterboxdURI',
    'tmdb_id': 'tmdbID',
    'imdb_id': 'imdbID',
    'title': 'Title',
    'year': 'Year',
    'directors': 'Directors',
    'rating': 'Rating',
    'rating10': 'Rating10',
    'watched_date': 'WatchedDate',
    'rewatch': 'Rewatch',
    'tags': 'Tags',
    'review': 'Review',
    'rank': 'Rank'
}

# Required columns - at least one must be present
REQUIRED_COLUMNS = ['LetterboxdURI', 'tmdbID', 'imdbID', 'Title']

# Basic validation rules
RATING_RANGE = (0.5, 5.0)  # Rating out of 5
RATING10_RANGE = (1, 10)   # Rating out of 10
DATE_FORMAT = 'YYYY-MM-DD'  # WatchedDate format
FILE_SIZE_LIMIT = '1MB'     # Maximum file size

# CSV export format column mappings
# https://letterboxd.com/about/importing-data/
CSV_FORMAT_COLUMNS = {
    "Letterboxd": {
        # Official Letterboxd import format
        "Title": "Title",
        "LetterboxdURI": "LetterboxdURI"
    },
    "TMDB": {
        # TMDB compatible format (used by import tools)
        "Title": "Name",
        "LetterboxdURI": "Letterboxd URI"
    }
}