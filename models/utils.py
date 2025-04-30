from core import requests, TagSoup
import csv
from io import StringIO

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
    """
    Generates a CSV syntax for the given movies.

    https://letterboxd.com/about/importing-data/
    https://letterboxd.com/list/new/

    Example:
        csv_data = get_csv_syntax(movie_list.movies)
        download_filename = movie_list.slug + '.csv'

        download_button = st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=download_filename,
            mime='text/csv'
        )

        Year,Title,LetterboxdURI
        2024,The Dark Knight,https://letterboxd.com/film/the-dark-knight/
        2023,The Shawshank Redemption,https://letterboxd.com/film/the-shawshank-redemption/
        2022,The Godfather,https://letterboxd.com/film/the-godfather/

    Returns:
        str: A CSV syntax for the given movies.
    """
    header = ['Year', 'Title', 'LetterboxdURI']
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    
    for movie in movies:
        writer.writerow([
            movie["Year"],
            movie["Title"],
            movie["LetterboxdURI"]
        ])
    
    return output.getvalue()