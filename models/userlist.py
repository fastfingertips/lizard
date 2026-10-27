from letterboxdpy.list import List
from letterboxdpy.utils.utils_csv import transform_to_ranked_movies


class UserList(List):
    """
    UserList class for handling Letterboxd user lists.
    Inherits from letterboxdpy's List for core functionality.
    """

    def __init__(self, url, username: str, slug: str):
        super().__init__(username, slug)
        self.url = getattr(url, "url", url)

    @property
    def movies(self) -> list:
        """Get list movies formatted for dataframe display."""
        return transform_to_ranked_movies(super().movies)

    @property
    def metadata(self) -> dict:
        """Get list metadata as dictionary."""
        return {
            "url": self.url,
            "username": self.username,
            "slug": self.slug,
            "title": self.title,
            "author": self.author,
            "count": self.count,
            "description": self.description,
            "date_created": self.date_created,
            "date_updated": self.date_updated,
            "tags": self.tags,
            "available": True,
        }
