from letterboxdpy.list import List
from letterboxdpy.utils.utils_csv import transform_to_ranked_movies


class UserList(List):
    """UserList class for handling Letterboxd user lists with filter support."""

    def __init__(self, username: str, slug: str, filters: str = ""):
        super().__init__(username, slug)
        if filters:
            clean_filters = filters.strip("/")
            self.filters = clean_filters
            self.url = f"{self.url}{clean_filters}/"
            self.pages.list.url = self.url
            self._movies = None

    @property
    def movies(self) -> list:
        """Get list movies formatted for dataframe display."""
        return transform_to_ranked_movies(super().movies)
