"""UserFilms model for handling Letterboxd user watched films."""

import contextlib
import re
from collections.abc import Callable

from letterboxdpy.pages.user_films import extract_movies_from_user_watched

from models.paginator import fetch_dom_with_retry, paginate_ranked_movies


class UserFilms:
    """UserFilms class for handling Letterboxd user watched films with filters."""

    FILMS_PER_PAGE = 72

    def __init__(self, username: str, filters: str = ""):
        self.username = username
        self.filters = filters.strip("/")
        clean_base = f"https://letterboxd.com/{username}/films/"
        self.url = f"{clean_base}{self.filters}/" if self.filters else clean_base
        self.title = f"{username}'s films"
        self._initial_dom = fetch_dom_with_retry(self.url)
        self.count = self._extract_count()
        self._movies = None

    def _extract_count(self) -> int:
        """Extract total movie count from heading or section tooltip."""
        with contextlib.suppress(Exception):
            dom = self._initial_dom
            if not dom:
                return 0

            heading = dom.find("p", class_="ui-block-heading")
            if heading:
                digits = re.search(r"watched\s+([\d,]+)", heading.get_text())
                if digits:
                    return int(digits.group(1).replace(",", ""))

            h1 = dom.find("h1", class_="section-heading")
            tooltip = h1.find("span", class_="tooltip") if h1 else None
            if tooltip and tooltip.get("title"):
                digits = re.search(r"[\d,]+", tooltip.get("title"))
                if digits:
                    return int(digits.group(0).replace(",", ""))
        return 0

    def fetch_movies(self, on_progress: Callable | None = None) -> list:
        """Scrape and return watched movies with optional progress callback."""
        if self._movies is None:
            self._movies = paginate_ranked_movies(
                base_url=self.url,
                items_per_page=self.FILMS_PER_PAGE,
                extractor_fn=extract_movies_from_user_watched,
                initial_dom=self._initial_dom,
                total_count=self.count,
                on_progress=on_progress,
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
        }
