from models.selectors import PageSelectors
from letterboxdpy.constants.project import DOMAIN_SHORT
from letterboxdpy.utils.utils_parser import get_meta_content

class DomParser:

    def __init__(self, dom):
        self.dom = dom

    def get_body_content(self, _obj) -> str:
        """
        a function that returns the content of the body tag..
        """
        #> get the content of the body tag.
        bodyContent = self.dom.find('body').attrs[_obj]
        return bodyContent

    def get_movie_count_from_meta(self, default=None) -> int:
        # Instead of making a GET request to the last page to retrieve the number of movies,
        # which could slow down the program, an alternative approach is employed.
        # The meta description of the list page is retrieved to obtain the count of movies.

        movie_count = default

        try:
            meta_description = get_meta_content(self.dom, name='description')

            for item in meta_description.split(' '):
                if item[0].isdigit():
                    movie_count = item
                    for char in item:
                        if not char.isdigit():
                            movie_count = movie_count.replace(char, '')
                    break

            movie_count = int(movie_count)
            if movie_count is not None:
                # print(f"Found the movie count in the meta description as {movie_count}.")
                return int(movie_count)
            else:
                # handle the case where no digit is found in the meta description
                print("Error: No digit found in the meta description.")
                return None
        except (AttributeError, TypeError) as e:
            print(f"Error while getting movie count from meta: {e}")
            return default

    def get_list_last_page(self, default=None) -> int:
        """
        Get the number of pages in the list (last page no)
        """

        last_page_no = default

        # repercussion
        try:
            # note: To find the number of pages, count the li's. Take the last number.
            # the text of the link in the last 'li' will give us how many pages our list is.
            # print('Checking the number of pages in the list..')
            # not created link when the number of movies is 100 or less in the list.
            last_page_no = int(self.dom.find(*PageSelectors.LAST_PAGE).find_all("li")[-1].a.text)
            # print(f'The list has more than one page ({last_page_no}).')
        except AttributeError: # exception when there is only one page.
            # print('There is no more than one page, this list is one page.')
            last_page_no = 1 # when the number of pages cannot be obtained, the number of pages is marked as 1.
        except Exception as e:
            print(f'An error occurred while checking the number of pages in the list. Error: {e}')
        finally:
            # print(f'Communication with the page is complete. It is learned that the number of pages in the list is {last_page_no}.')
            return last_page_no # aftermath

    def get_list_short_url(self, domain=DOMAIN_SHORT, default=None) -> str:
        """
        Get the short url of the list.
        """

        short_url = default

        # repercussion
        try:
            short_url = self.dom.find('input', type='text', value=lambda x: x and domain in x).attrs['value']
            print(f'Found the short url of the list as {short_url}.')
        except Exception as e:
            print(f'An error occurred while obtaining the short url of the list. Error: {e}')

        return short_url # aftermath