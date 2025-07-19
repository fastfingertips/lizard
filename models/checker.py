from letterboxdpy.utils.utils_url import check_url_match
from letterboxdpy.utils.utils_parser import get_meta_content, get_body_content
from typing import Optional, TypedDict


class ListMetaData(TypedDict):
    """Type definition for list metadata"""
    url: Optional[str]
    title: Optional[str]
    owner: Optional[str]
    is_available: bool
    error: Optional[str]

class Checker:
    """
    A class to check and validate Letterboxd list pages.
    Provides methods to verify list existence and extract metadata.
    """

    def __init__(self, dom):
        """
        Initialize the Checker with a DOM object.

        Args:
            dom: The BeautifulSoup DOM object to check
        """
        self.dom = dom

    def is_list(self) -> bool:
        """
        Checks if the current page is a valid Letterboxd list.

        Returns:
            bool: True if the page is a valid list, False otherwise
        """
        try:
            meta_content = get_meta_content(self.dom, property='og:type')
            return meta_content == 'letterboxd:list'
        except Exception as e:
            print(f"Error checking list type: {e}")
            return False
    
    def get_list_meta(self, url: str) -> ListMetaData:
        """
        Extracts metadata from a Letterboxd list page.
        
        Args:
            url: The original URL of the list
            
        Returns:
            ListMetaData: A dictionary containing list metadata and status
        """
        data: ListMetaData = {
            'url': None,
            'title': None,
            'owner': None,
            'is_available': False,
            'error': None
        }

        try:
            # Extract basic metadata
            list_url = get_meta_content(self.dom, property='og:url')
            list_title = get_meta_content(self.dom, property='og:title')
            list_owner = get_body_content(self.dom, 'data-owner')

            # Check for URL redirection
            if not check_url_match(url, list_url):
                print(f'Redirected to {list_url}')

            # Update metadata
            data.update({
                'url': list_url,
                'title': list_title,
                'owner': list_owner,
                'is_available': True
            })

        except AttributeError as e:
            data['error'] = f"Missing required metadata: {str(e)}"
            print(f"Metadata extraction error: {e}")
        except Exception as e:
            data['error'] = f"Unexpected error: {str(e)}"
            print(f"Unexpected error while checking the list: {e}")

        return data