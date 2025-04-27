import validators
from models.parser import DomParser
from models.utils import get_dom_from_url
from models.constants import (
    URL_PROTOCOLS,
    DOMAIN_SHORT,
    DOMAIN_MATCHES,
)


class Url():

    def __init__(self, url, url_dom=None):
        
        self.url = url
        self.detail_url = url + 'detail/'
        self.page_url = self.detail_url + 'page/'

        self._url_dom = url_dom
        self._detail_url_dom = None

        self.slug = get_list_slug(self.url)

        self._dom_parser = None
        self._detail_dom_parser = None

    @property
    def url_dom(self):
        if not self._url_dom:
            self._url_dom = get_dom_from_url(self.url)
            self._dom_parser = DomParser(self.url_dom)
        return self._url_dom
    
    @property
    def detail_url_dom(self):
        if not self._detail_url_dom:
            self._detail_url_dom = get_dom_from_url(self.detail_url)
            self._detail_dom_parser = DomParser(self._detail_url_dom)
        return self._detail_url_dom
    
    @property
    def dom_parser(self):
        if not self._dom_parser:
            self._dom_parser = DomParser(self.url_dom)
        return self._dom_parser
    
    @property
    def detail_dom_parser(self):
        if not self._detail_dom_parser:
            self._detail_dom_parser = DomParser(self.detail_url_dom)
        return self._detail_dom_parser


def check_url_match(base_url, target_url) -> bool:
    """
    this function checks if two URLs match,
    and returns a boolean value as the result.
    """
    return base_url == target_url or f'{base_url}/' == target_url

def is_short_url(url) -> bool:
    """
    this function checks if the URL is a short URL or not,
    and returns a boolean value as the result.
    """
    return any(prot+DOMAIN_SHORT in url for prot in URL_PROTOCOLS)

def is_url(url) -> bool:
    """
    this function checks if the URL is valid or not,
    and returns a boolean value as the result.
    """
    return validators.url(url)

def check_url_pattern(url) -> bool:
    """
    this function checks if the URL is a list or not,
    and returns a boolean value as the result.
    """    
    for match in DOMAIN_MATCHES:
        if match in url:
            match_index = url.index(match)
            protocol = url[:match_index]
            if protocol in URL_PROTOCOLS:
                # > URL pattern is valid
                return True
    # > Url pattern is invalid
    return False

def convert_to_pattern(url) -> str:
    """
    -> https://letterboxd.com/fastfingertips/list/list_name/
    <- fastfingertips/list/list_name/
    """
    for protocol in URL_PROTOCOLS:
        if protocol in url:
            for match in DOMAIN_MATCHES:
                if match in url:
                    if match == 'boxd.it/':
                        return url
                    url = url.replace(protocol+match, '')
                    return url
    return url

def get_list_slug(url) -> str:
    """
    extract the slug from a URL containing '/list/'.
    example: 'https://letterboxd.com/fastfingertips/list/list_name/' -> 'list_name'
    """
    return url[url.index('/list/') + len('/list/'):].replace('/', '')