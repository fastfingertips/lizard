from models.parser import DomParser
from models.utils import get_dom_from_url
import validators


class Url():

    domain_name = 'https://letterboxd.com/'

    def __init__(self, url, url_dom=None):
        
        self.url = url
        self.detail_url = url + 'detail/'
        self.page_url = self.detail_url + 'page/'

        self._url_dom = url_dom
        self._detail_url_dom = None

        self.slug = get_list_domain_name(self.url)

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

# -- FUNCTIONS --

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
    short_domain = 'boxd.it'
    protocols = ['http://', 'https://']
    return any(prot+short_domain in url for prot in protocols)

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

    matches = ['letterboxd.com/', 'boxd.it/']
    protocols = ['http://', 'https://']
    
    for match in matches:
        if match in url:
            match_index = url.index(match)
            protocol = url[:match_index]
            if protocol in protocols:
                print(f'URL pattern is valid. ({protocol})')
                return True
    print('URL pattern is invalid.')
    print(f'URL: {url}')
    return False

def convert_to_pattern(url) -> str:
    """
    -> https://letterboxd.com/fastfingertips/list/list_name/
    <- fastfingertips/list/list_name/
    """
    
    matches = ['letterboxd.com/', 'boxd.it/']
    protocols = ['http://', 'https://']

    print(f'Converting input: {url}')
    for protocol in protocols:
        if protocol in url:
            for match in matches:
                if match in url:
                    if match == 'boxd.it/':
                        return url
                    url = url.replace(protocol+match, '')
                    print(f'Converted URL: {url}')
                    return url
    print(f'Data is not letterboxd url. Not converted. ({url})')
    return url

def get_list_domain_name(url) -> str:
    """
    extract domain name from a URL containing '/list/'.
    example: 'https://letterboxd.com/fastfingertips/list/list_name/ -> 'fastfingertips'
    """
    return url[url.index('/list/') + len('/list/'):].replace('/', '')