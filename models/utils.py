from core import requests, TagSoup

def get_dom_from_url(_url) -> TagSoup:
    """
    Reads and retrieves the DOM of the specified page URL.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    try:
        #> Provides information in the log file at the beginning of the connection.
        print(f'Conection to the address [{_url}] is being established..')
        while True:
            #> https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
            try:
                urlResponseCode = requests.get(_url, headers=headers, timeout=30)
                urlDom = TagSoup(urlResponseCode.content.decode('utf-8'), 'html.parser')
                if urlDom is not None:
                    return urlDom # Returns the page DOM
            except requests.ConnectionError as e:
                print("OOPS!! Connection Error. Make sure you are connected to the Internet. Technical details are provided below.")
                print(str(e))
                continue
            except requests.Timeout as e:
                print("OOPS!! Timeout Error")
                print(str(e))
                continue
            except requests.RequestException as e:
                print("OOPS!! General Error")
                print(str(e))
                continue
            except KeyboardInterrupt:
                print("Someone closed the program")
            except Exception as e:
                print('Error:', e)
    except Exception as e:
        #> If an error occurs while obtaining the DOM...
        print(f'Connection to the address failed [{_url}] Error: {e}')

def get_csv_syntax(movies) -> str:
    # https://letterboxd.com/about/importing-data/
    # https://letterboxd.com/list/new/
    header = ['Year', 'Title', 'LetterboxdURI']
    csv_syntax = ','.join(header) + '\n'
    for movie in movies:
        csv_syntax += f'{movie["Year"]},{movie["Title"]},{movie["LetterboxdURI"]}\n'
    return csv_syntax