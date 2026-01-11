from letterboxdpy.pages.user_list import extract_movies
from letterboxdpy.pages import user_list
from letterboxdpy.utils.utils_csv import transform_to_ranked_movies


class UserList(user_list.UserList):
    """
    UserList class for handling Letterboxd user lists.
    Inherits from letterboxdpy's UserList for core functionality.
    """

    def __init__(self, url, username: str, slug: str):
        """
        Initialize UserList with URL, username, and slug.
        
        Args:
            url: URL object containing the list URL
            username: Letterboxd username
            slug: List slug identifier
        """
        super().__init__(username, slug)
        self.url = url.url
        self.username = username
        self.slug = slug

    def get_movies(self) -> list:
        """
        Get movies from user list.
        
        Returns:
            List of movies in ranked format
        """
        letterboxd_movies = extract_movies(self.url, items_per_page=self.LIST_ITEMS_PER_PAGE)
        return transform_to_ranked_movies(letterboxd_movies)

    @property
    def movies(self):
        """Property to get movies from user list."""
        return self.get_movies()
    
    @property
    def metadata(self):
        """
        Get list metadata as dictionary.
        
        Returns:
            Dictionary containing list metadata
        """
        return {
            'url': self.url,
            'username': self.username,
            'slug': self.slug,
            'title': super().get_title(),
            'author': super().get_author(),
            'count': super().get_count(),
            'description': super().get_description(),
            'date_created': super().get_date_created(),
            'date_updated': super().get_date_updated(),
            'tags': super().get_tags(),
            'available': True
        }
