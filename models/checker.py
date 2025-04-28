from models.parser import DomParser
from models.url import check_url_match

class Checker:

    def __init__(self, dom):
        self.dom = dom
        self.dom_parser = DomParser(dom)

    def is_list(self) -> bool:
        """
        Checks if the current page is a letterboxd list.
        Returns True if the page is a list, False otherwise.
        """
        meta_content = self.dom_parser.get_meta_content('og:type')
        return meta_content == 'letterboxd:list'
    
    def get_list_meta(self, url) -> dict:
        """
        Gets meta information about the list.
        Returns a dictionary with list metadata and availability status.
        """
        data = {'is_available': False}
        try:
            list_url = self.dom_parser.get_meta_content('og:url')
            list_title = self.dom_parser.get_meta_content('og:title')
            list_owner = self.dom_parser.get_body_content('data-owner')

            if not check_url_match(url, list_url):
                print(f'Redirected to {list_url}')

            data = {
                'url': list_url,
                'title': list_title,
                'owner': list_owner,
                'is_available': True
            }
        except Exception as e:
            print(f'An error occurred while checking the list. Error: {e}')
        return data