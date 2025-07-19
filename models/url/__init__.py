"""
URL package for URL handling and processing.

This package contains URL utilities for Letterboxd list processing.
"""

from letterboxdpy.utils.utils_url import get_list_slug
from letterboxdpy.core.scraper import parse_url


class Url():

    def __init__(self, url, url_dom=None):
        
        self.url = url
        self.detail_url = url + 'detail/'
        self.page_url = self.detail_url + 'page/'

        self._url_dom = url_dom
        self._detail_url_dom = None

        self.slug = get_list_slug(self.url)

    @property
    def url_dom(self):
        if not self._url_dom:
            self._url_dom = parse_url(self.url)
        return self._url_dom
    
    @property
    def detail_url_dom(self):
        if not self._detail_url_dom:
            self._detail_url_dom = parse_url(self.detail_url)
        return self._detail_url_dom
