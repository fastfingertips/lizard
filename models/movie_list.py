
from letterboxdpy.pages.user_list import extract_movies
from letterboxdpy.pages import user_list, user_watchlist


class WatchList:
    def __init__(self, url, username: str):
        self.url = url.url
        self.username = username

    def get_movies(self) -> list:
        """Get movies from watchlist"""
        letterboxd_movies = extract_movies(self.url, items_per_page=user_watchlist.UserWatchlist.FILMS_PER_PAGE)

        movies = []
        for rank, (_, movie_data) in enumerate(letterboxd_movies.items(), 1):
            movie = {
                "Rank": rank,
                "Title": movie_data.get('name', ''),
                "LetterboxdURI": movie_data.get('url', '')
            }
            movies.append(movie)
        return movies

    @property
    def movies(self):
        return self.get_movies()


class UserList:
    def __init__(self, url, username: str, slug: str):
        self.url = url.url
        self.username = username
        self.slug = slug

    def get_movies(self) -> list:
        """Get movies from user list"""
        letterboxd_movies = extract_movies(self.url, items_per_page=user_list.UserList.LIST_ITEMS_PER_PAGE)

        movies = []
        for rank, (_, movie_data) in enumerate(letterboxd_movies.items(), 1):
            movie = {
                "Rank": rank,
                "Title": movie_data.get('name', ''),
                "LetterboxdURI": movie_data.get('url', '')
            }
            movies.append(movie)
        return movies

    @property
    def movies(self):
        return self.get_movies()
