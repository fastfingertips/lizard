from collections.abc import Callable

from letterboxdpy.constants.project import DOMAIN
from letterboxdpy.utils.movies_extractor import extract_movies_from_vertical_list
from letterboxdpy.utils.utils_url import apply_sort_by_to_url, extract_path_segment
from letterboxdpy.watchlist import Watchlist

from models.paginator import fetch_dom_with_retry, paginate_ranked_movies


class WatchList(Watchlist):
    """WatchList class for handling Letterboxd user watchlists."""

    def __init__(
        self,
        target,
        username: str | None = None,
        filters: str = "",
        sort_by: str | None = None,
    ):
        """Initialize WatchList with username or User object, reusing cached count/DOM."""
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

        self.username = user
        self.filters = filters.strip("/") if filters else ""
        self.sort_by = sort_by
        self.pages = self.WatchlistPages(self.username, sort_by=self.sort_by)
        if self.filters:
            base_url = f"{DOMAIN}/{self.username}/watchlist/{self.filters}/"
            self.url = (
                apply_sort_by_to_url(base_url, self.sort_by)
                if self.sort_by
                else base_url
            )
            self.pages.watchlist.url = self.url
        else:
            self.url = self.get_url()
        self._initial_dom = None
        self._movies = None

        cached_len = getattr(target, "watchlist_length", None)
        if cached_len is not None:
            self.count = cached_len
            self.last_page = self.get_last_page()
        else:
            self._initial_dom = fetch_dom_with_retry(self.url)
            self.count = self._extract_count_from_dom(self._initial_dom)
            self.last_page = self.get_last_page()

    @staticmethod
    def _extract_count_from_dom(dom) -> int:
        """Extract watchlist film count from pre-fetched DOM."""
        if not dom:
            return 0
        wl_div = dom.find("div", class_="s-watchlist-content")
        if wl_div and "data-num-entries" in wl_div.attrs:
            return int(wl_div["data-num-entries"])
        count_span = dom.find("span", class_="js-watchlist-count")
        if count_span:
            return int(count_span.text.split()[0].replace(",", ""))
        return 0

    def fetch_movies(
        self,
        on_progress: Callable | None = None,
        max_pages: int | None = None,
    ) -> list:
        """Scrape watchlist movies with progress callback and initial DOM reuse."""
        if self._movies is None:
            total_count = None if self.filters else self.count
            self._movies = paginate_ranked_movies(
                base_url=self.url,
                items_per_page=self.pages.watchlist.FILMS_PER_PAGE,
                extractor_fn=extract_movies_from_vertical_list,
                initial_dom=self._initial_dom,
                total_count=total_count,
                on_progress=on_progress,
                max_pages=max_pages,
            )
        return self._movies

    @property
    def movies(self) -> list:
        """Get watchlist movies formatted for dataframe display."""
        return self.fetch_movies()
