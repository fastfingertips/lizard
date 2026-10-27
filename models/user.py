"""User model for handling Letterboxd user profiles and lists in Lizard."""

from fastfingertips.url_utils import extract_path_segment
from letterboxdpy.constants.project import DOMAIN
from letterboxdpy.core.scraper import parse_url
from letterboxdpy.pages.user_profile import UserProfile
from letterboxdpy.utils.lists_extractor import ListsExtractor


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
        self.profile = Profile(self.username)
        self.url = self.profile.url
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
        """Fetch user lists using canonical trailing slash URL with error handling."""
        try:
            url = f"{DOMAIN}/{self.username}/lists/"
            return ListsExtractor.from_url(url, max_lists)
        except Exception:
            return {"lists": {}, "count": 0}

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
