"""User model for handling Letterboxd user profiles and lists in Lizard."""

import contextlib
import re
import time
from collections.abc import Callable

from fastfingertips.url_utils import extract_path_segment
from letterboxdpy.constants.project import DOMAIN
from letterboxdpy.core.exceptions import AccessDeniedError, ResourceNotFoundError
from letterboxdpy.core.scraper import Scraper, parse_url
from letterboxdpy.utils.lists_extractor import ListsExtractor
from letterboxdpy.utils.utils_parser import get_list_last_page

from models.paginator import fetch_dom_with_retry, pace_request

# Clean up HTTP/2 protocol violation and set modern browser navigation headers
Scraper.headers.pop("connection", None)
Scraper.headers.update(
    {
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    }
)


class User:
    """User model representing a Letterboxd user in Lizard."""

    def __init__(self, target):
        self.username = self.extract_username(target)
        self.url = f"{DOMAIN}/{self.username}/"
        if not re.match(r"^[A-Za-z0-9_]+$", self.username):
            raise ResourceNotFoundError(self.url)
        self._initial_lists_dom = None
        self.lists_partial = False
        self.lists_fetched_count = 0
        self.lists_expected_pages = 1
        self.profile = None
        self.id = None
        self.badge = None
        self.display_name = self.username
        self.bio = None
        self.location = None
        self.website = None
        self.watchlist_length = None
        self.stats = {}
        self.favorites = None
        self.avatar = None
        self.backdrop = None
        self._populate_profile()

    def _populate_profile(self) -> None:
        """Populate profile metadata fast from lists and watchlist endpoints."""
        lists_url = f"{DOMAIN}/{self.username}/lists/"
        try:
            lists_dom = parse_url(lists_url)
        except AccessDeniedError:
            lists_dom = None
        except ResourceNotFoundError:
            raise ResourceNotFoundError(self.url) from None

        if lists_dom:
            self._initial_lists_dom = lists_dom
            ph = lists_dom.find("section", class_="profile-header")
            if ph:
                h1 = ph.find("h1")
                if h1:
                    self.display_name = h1.get_text(strip=True)

                badge_span = ph.find("span", class_="badge")
                if badge_span:
                    self.badge = badge_span.get_text(strip=True).lower()

                avatar_img = ph.find("img")
                if avatar_img and avatar_img.get("src"):
                    raw_src = avatar_img["src"]
                    upscaled = re.sub(
                        r"avtr-0-\d+-0-\d+-crop", "avtr-0-1000-0-1000-crop", raw_src
                    )
                    self.avatar = {
                        "exists": True,
                        "upscaled": True,
                        "url": upscaled,
                    }
                    segment = extract_path_segment(
                        raw_src, after="avatar/upload/", before="/shard"
                    )
                    if segment:
                        self.id = int(segment.replace("/", ""))

        with contextlib.suppress(Exception):
            wl_dom = fetch_dom_with_retry(f"{DOMAIN}/{self.username}/watchlist/")
            count_span = (
                wl_dom.find("span", class_="js-watchlist-count") if wl_dom else None
            )
            if count_span:
                digits = re.search(r"\d+", count_span.get_text().replace(",", ""))
                if digits:
                    self.watchlist_length = int(digits.group(0))

    @property
    def films_count(self) -> int | None:
        """Get total watched films count from profile stats or fallback scraper."""
        if self.stats and "films" in self.stats:
            return self.stats["films"]
        if not hasattr(self, "_films_count_fallback"):
            self._films_count_fallback = None
            with contextlib.suppress(Exception):
                from models.userfilms import UserFilms

                films = UserFilms(self.username)
                self._films_count_fallback = films.count if films.count > 0 else None
                if self._films_count_fallback and self.stats is not None:
                    self.stats["films"] = self._films_count_fallback
        return self._films_count_fallback

    @staticmethod
    def extract_username(target) -> str:
        """Extract and sanitize username from string, URL, or object."""
        if hasattr(target, "username") and target.username:
            raw = target.username
        elif isinstance(target, str):
            raw = target.strip()
            if "letterboxd.com/" in raw:
                extracted = extract_path_segment(
                    raw, after="letterboxd.com/", before="/"
                )
                raw = extracted if extracted else raw
        else:
            raw = str(target).strip()

        return raw.strip("/").lower()

    def get_lists(
        self, max_lists: int | None = None, on_progress: Callable | None = None
    ) -> dict:
        """Fetch user lists with canonical URLs, retry backoff, and polite pacing."""
        data = {"limit": False, "count": 0, "last_page": 1, "lists": {}}
        total_lists = self.stats.get("lists") if self.stats else None
        expected_pages = 1
        fetched_pages = 0
        page = 1

        while True:
            step_start = time.monotonic()
            used_cached = page == 1 and self._initial_lists_dom is not None
            page_url = (
                f"{DOMAIN}/{self.username}/lists/"
                if page == 1
                else f"{DOMAIN}/{self.username}/lists/page/{page}/"
            )
            dom = (
                self._initial_lists_dom
                if used_cached
                else fetch_dom_with_retry(page_url)
            )
            if not dom:
                break

            if page == 1:
                expected_pages = get_list_last_page(dom) or 1

            articles = dom.find_all("article", {"class": "list-summary"})
            if not articles:
                break

            fetched_pages = page

            for item in articles:
                list_data = ListsExtractor._extract_list_data(item)
                for entry in list_data.values():
                    if entry.get("url"):
                        entry["url"] = entry["url"].rstrip("/") + "/"
                data["lists"].update(list_data)

                if max_lists and len(data["lists"]) >= max_lists:
                    data["limit"] = True
                    break

            if on_progress is not None:
                on_progress(len(data["lists"]), total_lists, page, 12)

            if data["limit"] or len(articles) < 12 or page >= expected_pages:
                break

            page += 1
            if not used_cached:
                pace_request(step_start)

        data["count"] = len(data["lists"])
        data["last_page"] = fetched_pages or 1
        self.lists_fetched_count = data["count"]
        self.lists_expected_pages = expected_pages
        self.lists_partial = bool(not data["limit"] and fetched_pages < expected_pages)

        if not self.lists_partial and (
            "lists" not in self.stats or not self.stats["lists"]
        ):
            self.stats["lists"] = data["count"]

        return data

    def jsonify(self) -> dict:
        """Serialize user profile attributes for UI display."""
        return {
            "username": self.username,
            "url": self.url,
            "id": self.id,
            "badge": self.badge,
            "display_name": self.display_name,
            "bio": self.bio,
            "location": self.location,
            "website": self.website,
            "watchlist_length": self.watchlist_length,
            "stats": self.stats,
            "favorites": self.favorites,
            "avatar": self.avatar,
            "backdrop": self.backdrop,
        }
