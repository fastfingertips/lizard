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