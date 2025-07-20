from typing import Union

from models.selectors import PageSelectors


def catch_error_message(dom) -> Union[bool, str]:
    """
    Checks if the page contains an error message.
    Returns the error message as a string if found, False otherwise.
    """
    error_body = dom.find(*PageSelectors.ERROR_BODY)
    if error_body:
        error_section = dom.find(*PageSelectors.ERROR_MESSAGE)
        if error_section:
            err = error_section.p.get_text()
            return err.split('\n')[0].strip()
    return False
