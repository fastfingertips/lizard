"""UserFilms model for handling Letterboxd user watched films."""

from collections.abc import Callable

from letterboxdpy.pages.user_films import (
    UserFilms as BaseUserFilms,
)
from letterboxdpy.pages.user_films import (
    extract_movies_from_user_watched,
)

from models.paginator import paginate_ranked_movies


class UserFilms(BaseUserFilms):
    """UserFilms class for handling Letterboxd user watched films with filters."""

    def __init__(
        self,
        username: str,
        filters: str = "",
        sort_by: str | None = None,
    ):
        clean_filters = filters.strip("/") if isinstance(filters, str) else filters
        super().__init__(username=username, filters=clean_filters, sort_by=sort_by)
        self.title = f"{username}'s films"
        self.count = self.get_count()
        self.last_page = self.get_last_page(self.count)
        self._movies = None

    def fetch_movies(
        self,
        on_progress: Callable | None = None,
        max_pages: int | None = None,
    ) -> list:
        """Scrape and return watched movies with optional progress callback."""
        if self._movies is None:
            self._movies = paginate_ranked_movies(
                base_url=self.url,
                items_per_page=self.FILMS_PER_PAGE,
                extractor_fn=extract_movies_from_user_watched,
                initial_dom=self._dom,
                total_count=self.count,
                on_progress=on_progress,
                max_pages=max_pages,
            )
        return self._movies

    @property
    def movies(self) -> list:
        """Scrape and return all watched movies across pages."""
        return self.fetch_movies()

    def jsonify(self) -> dict:
        """Serialize user films metadata for UI display."""
        return {
            "username": self.username,
            "url": self.url,
            "count": self.count,
            "filters": self.filters or None,
            "sort_by": self.sort_by,
        }
