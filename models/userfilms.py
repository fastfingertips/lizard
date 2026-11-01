"""UserFilms model for handling Letterboxd user watched films."""

import contextlib
import re

from letterboxdpy.core.scraper import parse_url
from letterboxdpy.pages.user_films import extract_movies_from_user_watched
from letterboxdpy.utils.utils_url import get_page_url


class UserFilms:
    """UserFilms class for handling Letterboxd user watched films with filters."""

    def __init__(self, username: str, filters: str = ""):
        self.username = username
        self.filters = filters.strip("/")
        clean_base = f"https://letterboxd.com/{username}/films/"
        self.url = f"{clean_base}{self.filters}/" if self.filters else clean_base
        self.title = f"{username}'s films"
        self.count = self._extract_count()
        self._movies = None

    def _extract_count(self) -> int:
        """Extract total movie count from heading or section tooltip."""
        with contextlib.suppress(Exception):
            dom = parse_url(self.url)
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

    @property
    def movies(self) -> list:
        """Scrape and return all watched movies across pages."""
        if self._movies is None:
            movies = []
            page = 1
            while True:
                page_url = get_page_url(self.url, page)
                dom = parse_url(page_url)
                scraped = extract_movies_from_user_watched(dom)
                if not scraped:
                    break

                for slug, m in scraped.items():
                    movies.append(
                        {
                            "Rank": len(movies) + 1,
                            "Title": m.get("name", slug),
                            "LetterboxdURI": m.get(
                                "url", f"https://letterboxd.com/film/{slug}/"
                            ),
                        }
                    )

                if len(scraped) < 72:
                    break
                page += 1

            self._movies = movies
        return self._movies

    def jsonify(self) -> dict:
        """Serialize user films metadata for UI display."""
        return {
            "username": self.username,
            "url": self.url,
            "count": self.count,
            "filters": self.filters or None,
        }
