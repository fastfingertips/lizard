from letterboxdpy.constants.project import URL_PROTOCOLS, DOMAIN_MATCHES


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

