from core import validators
from letterboxdpy.constants.project import URL_PROTOCOLS, DOMAIN_SHORT, DOMAIN_MATCHES


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