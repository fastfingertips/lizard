"""
Letterboxd movie list data extraction and processing.

Extends the Url class to extract movie data from Letterboxd lists,
including titles, years, rankings, and metadata with pagination support.
"""

import time
import streamlit as st
from stqdm import stqdm

from letterboxdpy.core.scraper import parse_url
from letterboxdpy.constants.project import DOMAIN
from letterboxdpy.utils.utils_parser import get_meta_content, get_body_content, get_movie_count_from_meta, get_list_last_page, get_list_short_url
from letterboxdpy.constants.selectors import FilmSelectors
from models.url import Url


class MovieList(Url):

    def __init__(self, url):
        super().__init__(url.url, url.url_dom)
        self._short_url = None
        self.title = self.get_list_title()
        self.owner = self.get_list_owner()
        self._movies = [] 
        self.last_page = get_list_last_page(self.detail_url_dom)
        self.movie_count = get_movie_count_from_meta(self.url_dom)

    def get_movies(self, caching = False) -> list:

        if caching:
            progress_text = 'Getting movies from list..'
            my_bar = st.progress(0, text=progress_text)

        movie_rank = 1

        for current_page_index in stqdm(range(int(self.last_page)), desc='Getting movies from list..'):
            list_current_page_url = self.page_url + str(current_page_index + 1) # .../list/.../detail/page/1
            if current_page_index:
                current_page_dom = parse_url(list_current_page_url)
            else:
                # if current page is first page, use already pulled dom
                if self.detail_url_dom is not None:
                    current_page_dom = self.detail_url_dom

            try:
                # getting' films/posters container (<ul> element)
                film_list = current_page_dom.find(*FilmSelectors.LIST)

                # above line is tryin' to get container, if it's None, tryin' alternative ways to get it
                alternative_ways = ['ul.film-list', 'ul.poster-list', 'ul.film-details-list']

                for current_alternative in alternative_ways:
                    if film_list is None: 
                        film_list = current_page_dom.select_one(current_alternative)
                    else:
                        # print(f'{movie_rank} and after film/poster container pulled without alternative help.')
                        break
                else:
                    if film_list is None:
                        print(f'{movie_rank} and after film/poster container could not be pulled.')
                        # ISSUE PINNED:
                    else:
                        print(f'{movie_rank} and after film/poster container pulled with alternative help.')

                # FILM POSTERS CONTAINER
                film_articles = film_list.find_all("article")

                for film_article in film_articles:

                    # MOVIE NAME AND YEAR CONTAINER
                    movie_headline_element = film_article.find(*FilmSelectors.HEADLINE)
                    movie_link_element = movie_headline_element.find('a')

                    # MOVIE NAME
                    movie_name = movie_link_element.text

                    # MOVIE LINK
                    movie_link = DOMAIN + movie_link_element.get('href') 

                    # MOVIE YEAR
                    try:
                        movie_year = film_article.find(*FilmSelectors.YEAR).text.strip()
                    except:
                        # Movie year could not be pulled. Check link: {movie_link}
                         movie_year = ''

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
            self._short_url = get_list_short_url(self.detail_url_dom)
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
        list_url = get_meta_content(self.url_dom, property='og:url')
        return list_url

    def get_list_title(self) -> str:
        list_title = get_meta_content(self.url_dom, property='og:title')
        return list_title

    def get_list_owner(self) -> str:
        list_owner = get_body_content(self.url_dom, 'data-owner')
        return list_owner