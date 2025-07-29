def transform_to_ranked_movies(letterboxd_movies: dict) -> list:
    """
    Transform letterboxd movies to ranked list format.
    
    Args:
        letterboxd_movies: Dictionary of movies from letterboxdpy
        
    Returns:
        List of movies with rank, title, and URI
    """
    movies = []
    for rank, (_, movie_data) in enumerate(letterboxd_movies.items(), 1):
        movie = {
            "Rank": rank,
            "Title": movie_data.get('name', ''),
            "LetterboxdURI": movie_data.get('url', '')
        }
        movies.append(movie)
    return movies