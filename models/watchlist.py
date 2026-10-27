from letterboxdpy.utils.utils_csv import transform_to_ranked_movies
from letterboxdpy.utils.utils_url import extract_path_segment
from letterboxdpy.watchlist import Watchlist


class WatchList(Watchlist):
    """
    WatchList class for handling Letterboxd user watchlists.
    Inherits from letterboxdpy's Watchlist for core functionality.
    """

    def __init__(self, target, username: str | None = None):
        """Initialize WatchList with username or URL."""
        if username:
            user = username
        elif hasattr(target, "username") and target.username:
            user = target.username
        elif isinstance(target, str) and "letterboxd.com" in target:
            extracted = extract_path_segment(target, after="letterboxd.com/")
            user = extracted if extracted else target
        else:
            user = str(target)

        super().__init__(user)
        if hasattr(target, "url"):
            self.url = target.url

    @property
    def movies(self) -> list:
        """Get watchlist movies formatted for dataframe display."""
        return transform_to_ranked_movies(super().movies)

    @property
    def metadata(self) -> dict:
        """Get watchlist metadata as dictionary."""
        return {
            "url": self.url,
            "username": self.username,
            "count": self.count,
            "owner": self.get_owner(),
            "available": True,
        }
