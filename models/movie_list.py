from core import st, time, stqdm

from models.utils import get_dom_from_url
from models.selectors import FilmSelectors
from models.url import Url


class MovieList(Url):

        def __init__(self, url):
            super().__init__(url.url, url.url_dom)
            self._short_url = None
            self.title = self.get_list_title()
            self.owner = self.get_list_owner()
            self._movies = [] 
            self.last_page = self.detail_dom_parser.get_list_last_page()
            self.movie_count = self.dom_parser.get_movie_count_from_meta()

        def get_movies(self, caching = False) -> list:

            print('Fetching movies from list..')

            if caching:
                progress_text = 'Getting movies from list..'
                my_bar = st.progress(0, text=progress_text)

            movie_rank = 1

            for current_page_index in stqdm(range(int(self.last_page)), desc='Getting movies from list..'):
                list_current_page_url = self.page_url + str(current_page_index + 1) # .../list/.../detail/page/1
                print(list_current_page_url)
                if current_page_index:
                    current_page_dom = get_dom_from_url(list_current_page_url)
                else:
                    # if current page is first page, use already pulled dom
                    if self.detail_url_dom is not None:
                        current_page_dom = self.detail_url_dom

                try:
                    # getting' films/posters container (<ul> element)
                    filmDetailsList = current_page_dom.find(*FilmSelectors.LIST)

                    # above line is tryin' to get container, if it's None, tryin' alternative ways to get it
                    alternative_ways = ['ul.film-list', 'ul.poster-list', 'ul.film-details-list']

                    for current_alternative in alternative_ways:
                        if filmDetailsList is None: 
                            filmDetailsList = current_page_dom.select_one(current_alternative)
                        else:
                            # print(f'{movie_rank} and after film/poster container pulled without alternative help.')
                            break
                    else:
                        if filmDetailsList is None:
                            print(f'{movie_rank} and after film/poster container could not be pulled.')
                            # ISSUE PINNED:
                        else:
                            print(f'{movie_rank} and after film/poster container pulled with alternative help.')

                    # FILM POSTERS CONTAINER
                    filmDetails = filmDetailsList.find_all("li")

                    for currentFilmDetail in filmDetails:

                        # MOVIE NAME AND YEAR CONTAINER
                        movieHeadlineElement = currentFilmDetail.find(*FilmSelectors.HEADLINE)
                        movieLinkElement = movieHeadlineElement.find('a')

                        # MOVIE NAME
                        movie_name = movieLinkElement.text

                        # MOVIE LINK
                        movie_link = 'https://letterboxd.com' + movieLinkElement.get('href') 

                        # MOVIE YEAR
                        try:
                            movie_year = movieHeadlineElement.find('small').text
                        except:
                            movie_year = ''
                            print(f'Movie year could not be pulled. Check link: {movie_link}')

                        # ADD MOVIE TO MOVIES LIST
                        self._movies.append({
                            "Rank": movie_rank,
                            "Year": movie_year,
                            "Title": movie_name,
                            "LetterboxdURI": movie_link
                        })
                        movie_rank += 1
                    if caching:
                        # fix the last percentage
                        current_percentage = int(100 / self.last_page) * (current_page_index + 1)
                        if self.last_page == current_page_index+1:
                            if int(100 / self.last_page) * self.last_page != 100:
                                current_percentage = 100
                
                        my_bar.progress(current_percentage, text=progress_text)
                except Exception as e:
                    print(f'An error was encountered while obtaining movie information. Error: {e}')
            if caching:
                time.sleep(.4)
                my_bar.empty()
            return self._movies

        @property
        def short_url(self):
            """
            this function checks short_url is avaliable or not,
            and returns short_url as result.
            """
            if self._short_url:
                return self._short_url
            else:
                self._short_url = self.dom_parser.get_list_short_url()
                return self._short_url

        @property
        def movies(_self):
            """
            this function checks movies is avaliable or not,
            and returns movies as result.
            """
            if _self._movies:
                return _self._movies
            else:
                _self._movies = _self.get_movies()
                return _self._movies

        def get_list_url(self) -> str:
            list_url = self.dom_parser.get_meta_content('og:url')
            return list_url

        def get_list_title(self) -> str:
            list_title = self.dom_parser.get_meta_content('og:title')
            return list_title

        def get_list_owner(self) -> str:
            list_owner = self.dom_parser.get_body_content('data-owner')
            return list_owner