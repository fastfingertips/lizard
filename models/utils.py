import csv
from io import StringIO

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