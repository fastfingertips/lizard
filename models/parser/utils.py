from typing import Union


def catch_error_message(url_dom) -> Union[bool, str]:
    """
    Checks if the page contains an error message.
    Returns the error message as a string if found, False otherwise.
    """
    err = url_dom.find('body', class_='error')
    if err:
        err = url_dom.find('section', class_='message').p.get_text()
        err = err.split('\n')[0].strip()
        return err
    return False
