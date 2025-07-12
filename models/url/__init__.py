from models.parser import DomParser
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

        self._dom_parser = None
        self._detail_dom_parser = None

    @property
    def url_dom(self):
        if not self._url_dom:
            self._url_dom = parse_url(self.url)
            self._dom_parser = DomParser(self.url_dom)
        return self._url_dom
    
    @property
    def detail_url_dom(self):
        if not self._detail_url_dom:
            self._detail_url_dom = parse_url(self.detail_url)
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