from collections.abc import Callable

from letterboxdpy.utils.movies_extractor import extract_movies_from_vertical_list
from letterboxdpy.utils.utils_url import extract_path_segment
from letterboxdpy.watchlist import Watchlist

from models.paginator import paginate_ranked_movies


class WatchList(Watchlist):
    """WatchList class for handling Letterboxd user watchlists."""

    def __init__(self, target, username: str | None = None):
        """Initialize WatchList with username or URL."""
        if username:
            user = username
        elif hasattr(target, "username") and target.username:
            user = target.username
        elif isinstance(target, str) and "letterboxd.com" in target:
            extracted = extract_path_segment(
                target, after="letterboxd.com/", before="/"
            )
            user = extracted if extracted else target
        else:
            user = str(target)

        super().__init__(user)

    def fetch_movies(self, on_progress: Callable | None = None) -> list:
        """Scrape watchlist movies with progress callback."""
        if self._movies is None:
            self._movies = paginate_ranked_movies(
                base_url=self.url,
                items_per_page=self.pages.watchlist.FILMS_PER_PAGE,
                extractor_fn=extract_movies_from_vertical_list,
                total_count=self.count,
                on_progress=on_progress,
            )
        return self._movies

    @property
    def movies(self) -> list:
        """Get watchlist movies formatted for dataframe display."""
        return self.fetch_movies()
