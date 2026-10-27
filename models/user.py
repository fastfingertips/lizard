"""User model for handling Letterboxd user profiles and lists in Lizard."""

from fastfingertips.url_utils import extract_path_segment
from letterboxdpy.constants.project import DOMAIN
from letterboxdpy.user import User as LetterboxdUser
from letterboxdpy.utils.lists_extractor import ListsExtractor


class User(LetterboxdUser):
    """User class for handling Letterboxd user profiles in Lizard."""

    def __init__(self, target):
        """Initialize User with username, profile URL, or object."""
        clean_username = self.extract_username(target)
        super().__init__(clean_username)

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
