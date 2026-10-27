from letterboxdpy.list import List
from letterboxdpy.utils.utils_csv import transform_to_ranked_movies


class UserList(List):
    """UserList class for handling Letterboxd user lists."""

    def __init__(self, username: str, slug: str):
        super().__init__(username, slug)

    @property
    def movies(self) -> list:
        """Get list movies formatted for dataframe display."""
        return transform_to_ranked_movies(super().movies)
