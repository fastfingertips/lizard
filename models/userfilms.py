"""UserFilms model for handling Letterboxd user watched films."""

import contextlib
import re
import time

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
        self._initial_dom = None
        self.count = self._extract_count()
        self._movies = None

    def _get_initial_dom(self):
        """Fetch and cache initial page DOM with retry backoff."""
        if self._initial_dom is None:
            for attempt in range(3):
                try:
                    self._initial_dom = parse_url(self.url)
                    break
                except Exception:
                    if attempt == 2:
                        break
                    time.sleep(1.0 * (attempt + 1))
        return self._initial_dom

    def _extract_count(self) -> int:
        """Extract total movie count from heading or section tooltip."""
        with contextlib.suppress(Exception):
            dom = self._get_initial_dom()
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

    @property
    def movies(self) -> list:
        """Scrape and return all watched movies across pages with resilient pacing."""
        if self._movies is None:
            movies = []
            page = 1
            while True:
                if page == 1 and self._initial_dom is not None:
                    dom = self._initial_dom
                else:
                    page_url = get_page_url(self.url, page)
                    dom = None
                    for attempt in range(3):
                        try:
                            dom = parse_url(page_url)
                            break
                        except Exception:
                            if attempt == 2:
                                break
                            time.sleep(1.0 * (attempt + 1))

                if not dom:
                    break

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
                time.sleep(0.5)

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
