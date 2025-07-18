from letterboxdpy.constants.project import DOMAIN_SHORT

class DomParser:

    def __init__(self, dom):
        self.dom = dom

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