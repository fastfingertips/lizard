from collections.abc import Callable

from letterboxdpy.list import List
from letterboxdpy.utils.movies_extractor import extract_movies_from_vertical_list
from letterboxdpy.utils.utils_url import apply_sort_by_to_url

from models.paginator import paginate_ranked_movies


class UserList(List):
    """UserList class for handling Letterboxd user lists with filter support."""

    def __init__(
        self,
        username: str,
        slug: str,
        filters: str = "",
        sort_by: str | None = None,
    ):
        super().__init__(username, slug, sort_by=sort_by)
        self.filters = ""
        if filters:
            clean_filters = filters.strip("/")
            self.filters = clean_filters
            base_url = (
                f"https://letterboxd.com/{self.username}/list/"
                f"{self.slug}/{clean_filters}/"
            )
            self.url = (
                apply_sort_by_to_url(base_url, self.sort_by)
                if self.sort_by
                else base_url
            )
            self.pages.list.url = self.url
            self._movies = None

    def fetch_movies(
        self,
        on_progress: Callable | None = None,
        max_pages: int | None = None,
    ) -> list:
        """Scrape list movies with progress callback and initial DOM reuse."""
        if self._movies is None:
            initial_dom = None if self.filters else self.pages.list.dom
            total_count = None if self.filters else self.count
            self._movies = paginate_ranked_movies(
                base_url=self.url,
                items_per_page=self.pages.list.FILMS_PER_PAGE,
                extractor_fn=extract_movies_from_vertical_list,
                initial_dom=initial_dom,
                total_count=total_count,
                on_progress=on_progress,
                max_pages=max_pages,
            )
        return self._movies

    @property
    def movies(self) -> list:
        """Get list movies formatted for dataframe display."""
        return self.fetch_movies()
