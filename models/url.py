"""
URL handling and processing utilities.

Method ordering follows dependency logic: methods that are used by other methods
are defined first, followed by methods that use them.
"""

from letterboxdpy.utils.utils_url import get_list_slug
from letterboxdpy.core.scraper import parse_url
from letterboxdpy.constants.project import URL_PROTOCOLS, DOMAIN_MATCHES


class Url():
    """URL handler for Letterboxd list processing."""

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

    @staticmethod
    def check_url_pattern(url) -> bool:
        """
        Check if the URL is a valid Letterboxd list.
        Returns True if URL pattern is valid, False otherwise.
        """
        for match in DOMAIN_MATCHES:
            if match in url:
                match_index = url.index(match)
                protocol = url[:match_index]
                if protocol in URL_PROTOCOLS:
                    return True
        return False

    @staticmethod
    def convert_to_pattern(url) -> str:
        """
        Convert full URL to pattern format.
        Example: https://letterboxd.com/user/list/test/ -> user/list/test/
        """
        for protocol in URL_PROTOCOLS:
            if protocol in url:
                for match in DOMAIN_MATCHES:
                    if match in url:
                        if match == 'boxd.it/':
                            return url
                        url = url.replace(protocol + match, '')
                        return url
        return url

    def check_pattern(self, url=None) -> bool:
        """
        Check if URL is valid Letterboxd list.
        Uses own URL if none provided.
        """
        target_url = url if url is not None else self.url
        return self.check_url_pattern(target_url)

    def to_pattern(self, url=None) -> str:
        """
        Convert URL to pattern format.
        Uses own URL if none provided.
        """
        target_url = url if url is not None else self.url
        return self.convert_to_pattern(target_url)
