"""User model for handling Letterboxd user profiles and lists in Lizard."""

import contextlib
import re
import time

from fastfingertips.url_utils import extract_path_segment
from letterboxdpy.constants.project import DOMAIN
from letterboxdpy.core.exceptions import AccessDeniedError
from letterboxdpy.core.scraper import Scraper, parse_url
from letterboxdpy.pages.user_profile import UserProfile
from letterboxdpy.utils.lists_extractor import ListsExtractor

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


class Profile(UserProfile):
    """UserProfile with canonical trailing slash URL."""

    def __init__(self, username: str) -> None:
        self.username = username
        self.url = f"{DOMAIN}/{self.username}/"
        self.dom = parse_url(self.url)


class User:
    """User model representing a Letterboxd user in Lizard."""

    def __init__(self, target):
        self.username = self.extract_username(target)
        self.url = f"{DOMAIN}/{self.username}/"
        try:
            self.profile = Profile(self.username)
            self.id = self.profile.get_id()
            self.badge = self.profile.get_badge()
            self.display_name = self.profile.get_display_name()
            self.bio = self.profile.get_bio()
            self.location = self.profile.get_location()
            self.website = self.profile.get_website()
            self.watchlist_length = self.profile.get_watchlist_length()
            self.stats = self.profile.get_stats()
            self.favorites = self.profile.get_favorites()
            self.avatar = self.profile.get_avatar()
            self.backdrop = self.profile.get_backdrop()
        except AccessDeniedError:
            self._populate_fallback()

    def _populate_fallback(self) -> None:
        """Populate profile metadata from accessible endpoints when profile is challenged."""
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

        with contextlib.suppress(Exception):
            lists_dom = parse_url(f"{DOMAIN}/{self.username}/lists/")
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
            wl_dom = parse_url(f"{DOMAIN}/{self.username}/watchlist/")
            count_span = wl_dom.find("span", class_="js-watchlist-count")
            if count_span:
                digits = re.search(r"\d+", count_span.get_text().replace(",", ""))
                if digits:
                    self.watchlist_length = int(digits.group(0))

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

    def get_lists(self, max_lists: int | None = None) -> dict:
        """Fetch user lists with canonical URLs, retry backoff, and polite pacing."""
        data = {"limit": False, "count": 0, "last_page": 1, "lists": {}}
        page = 1

        while True:
            page_url = (
                f"{DOMAIN}/{self.username}/lists/"
                if page == 1
                else f"{DOMAIN}/{self.username}/lists/page/{page}/"
            )
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

            articles = dom.find_all("article", {"class": "list-summary"})
            if not articles:
                break

            for item in articles:
                list_data = ListsExtractor._extract_list_data(item)
                data["lists"].update(list_data)

                if max_lists and len(data["lists"]) >= max_lists:
                    data["limit"] = True
                    break

            if data["limit"] or len(articles) < 12:
                break

            page += 1
            time.sleep(0.5)

        data["count"] = len(data["lists"])
        data["last_page"] = page

        if "lists" not in self.stats or not self.stats["lists"]:
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
