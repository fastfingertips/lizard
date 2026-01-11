from letterboxdpy.pages.user_list import extract_movies
from letterboxdpy.pages import user_watchlist
from letterboxdpy.utils.utils_csv import transform_to_ranked_movies


class WatchList(user_watchlist.UserWatchlist):
    """
    WatchList class for handling Letterboxd user watchlists.
    Inherits from letterboxdpy's UserWatchlist for core functionality.
    """

    def __init__(self, url, username: str):
        """
        Initialize WatchList with URL and username.
        
        Args:
            url: URL object containing the watchlist URL
            username: Letterboxd username
        """
        super().__init__(username)
        self.url = url.url
        self.username = username

    def get_movies(self) -> list:
        """
        Get movies from watchlist.
        
        Returns:
            List of movies in ranked format
        """
        letterboxd_movies = extract_movies(self.url, items_per_page=self.FILMS_PER_PAGE)
        return transform_to_ranked_movies(letterboxd_movies)

    @property
    def movies(self):
        """Property to get movies from watchlist."""
        return self.get_movies()
    
    @property
    def metadata(self):
        """
        Get watchlist metadata as dictionary.
        
        Returns:
            Dictionary containing watchlist metadata
        """
        return {
            'url': self.url,
            'username': self.username,
            'count': super().get_count(),
            'owner': super().get_owner(),
            'available': True
        }
