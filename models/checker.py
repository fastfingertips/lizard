from models.parser import DomParser
from models.url import check_url_match

class Checker:

    def __init__(self, dom):
        self.dom = dom
        self.dom_parser = DomParser(dom)

    def check_page_is_list(self) -> bool:
        """
        this function checks dom's meta tag,
        og:type is letterboxd:list or not,
        and returns bool value as result.
        """

        meta_content = self.dom_parser.get_meta_content('og:type')

        context = {
            'is_list': meta_content == 'letterboxd:list',
            'meta_content': meta_content
            }
        return context
    
    def user_list_check(self, url) -> dict:
        try:
            list_url = self.dom_parser.get_meta_content('og:url')
            list_title = self.dom_parser.get_meta_content('og:title')
            list_owner = self.dom_parser.get_body_content('data-owner')

            if not check_url_match(url, list_url):
                print(f'Redirected to {list_url}')

            context = {
                'list_url': list_url,
                'list_title': list_title,
                'list_owner': list_owner,
                'list_avaliable': True,
            }
        except Exception as e:
            print(f'An error occurred while checking the list. Error: {e}')
            context = {
                'list_avaliable': False
            }
        finally:
            return context
