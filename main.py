from bs4 import BeautifulSoup as TagSoup
import streamlit as st
import pandas as pd
import requests
from paths import paths
import time

def get_dom_from_url(_url) -> TagSoup:
    """
    Reads and retrieves the DOM of the specified page URL.
    """
    try:
        #> Provides information in the log file at the beginning of the connection.
        print(f'Trying to connect to {_url}..')
        while True:
            #> https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
            try:
                urlResponseCode = requests.get(_url, timeout=30)
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

def get_body_content(_dom, _obj) -> str:
    """
    a function that returns the content of the body tag..
    """
    #> get the content of the body tag.
    bodyContent = _dom.find('body').attrs[_obj]
    return bodyContent

def get_list_domain_name(_url) -> str:
    return _url[_url.index('/list/')+len('/list/'):].replace('/','')

def get_list_last_page(_detail_dom, _detail_url) -> int:
    """
    Get the number of pages in the list (last page no)
    """
    try:
        # note: To find the number of pages, count the li's. Take the last number.
        # the text of the link in the last 'li' will give us how many pages our list is.
        print('Checking the number of pages in the list..')
        # not created link when the number of movies is 100 or less in the list.
        last_page_no = _detail_dom.find(*paths['last_page_no']).find_all("li")[-1].a.text 
        print(f'The list has more than one page ({last_page_no}).')
    except AttributeError: # exception when there is only one page.
        print('There is no more than one page, this list is one page.')
        last_page_no = 1 # when the number of pages cannot be obtained, the number of pages is marked as 1.
        print(last_page_no, _detail_dom, _detail_url) # send page info.
    except Exception as e:
        print(f'An error occurred while checking the number of pages in the list. Error: {e}')
    finally:
        print(f'Communication with the page is complete. It is learned that the number of pages in the list is {last_page_no}.')
        return int(last_page_no)

def get_movie_count_from_meta_description(_list_dom) -> int:
    print('Getting the number of movies on the list meta description.')
    # Instead of connecting to the last page and getting the number of movies on the last page, which generates a GET request
    # and slows down the program, an alternative approach is used by getting the meta description of the list page.
    metaDescription = _list_dom.find(*paths['meta_description']).attrs['content']
    metaDescription = metaDescription[10:] # after 'A list of' in the description

    for i in range(6):
        try:
            int(metaDescription[i])
            ii = i+1
        except: pass
    movie_count = metaDescription[:ii]
    return movie_count

def get_movie_count_from_list_last_page(_last_page_no, _detail_url) -> int:
    print('Getting the number of movies on the list last page.')
    try:
        last_page_dom = get_dom_from_url(f'{_detail_url}{_last_page_no}')
        last_page_articles = last_page_dom.find(*paths['last_page_articles']).find_all("li")
        last_page_movie_count =  len(last_page_articles) # film count
        movie_count = ((int(_last_page_no)-1)*100)+last_page_movie_count # total movie count
        print(f"Found list movie count as {movie_count}.")
        return movie_count
    except Exception as e:
        print(f'An error occurred while obtaining the number of movies on the list last page. Error: {e}')

def get_movies_from_url(_list_detail_page_url, _last_page_no) -> list:
    progress_text = 'Getting movies from list..'
    my_bar = st.progress(0, text=progress_text)
    movie_rank = 1
    movies = []

    for current_page_index in range(int(_last_page_no)):
        list_current_page_url = _list_detail_page_url + str(current_page_index + 1) # .../list/.../detail/page/1
        current_page_dom = get_dom_from_url(list_current_page_url)

        try:
            # getting' films/posters container (<ul> element)
            filmDetailsList = current_page_dom.find(*paths['film_detail_list_ul'])
            # above line is tryin' to get container, if it's None, tryin' alternative ways to get it
            alternative_ways = ['ul.film-list', 'ul.poster-list', 'ul.film-details-list']

            for current_alternative in alternative_ways:
                if filmDetailsList is None: 
                    filmDetailsList = current_page_dom.select_one(current_alternative)
                else:
                    # print(f'{movie_rank} and after film/poster container pulled without alternative help.')
                    break
            else:
                if filmDetailsList is None:
                    print(f'{movie_rank} and after film/poster container could not be pulled.')
                    # ISSUE PINNED:
                else:
                    print(f'{movie_rank} and after film/poster container pulled with alternative help.')

            # FILM POSTERS CONTAINER
            filmDetails = filmDetailsList.find_all("li")

            for currentFilmDetail in filmDetails:

                # MOVIE NAME AND YEAR CONTAINER
                movieHeadlineElement = currentFilmDetail.find(*paths['movie_headline_element'])
                movieLinkElement = movieHeadlineElement.find('a')

                # MOVIE NAME
                movieName = movieLinkElement.text
               
                # MOVIE LINK
                movieLink = 'https://letterboxd.com' + movieLinkElement.get('href') 

                # MOVIE YEAR
                try:
                    movieYear = movieHeadlineElement.find('small').text
                except:
                    movieYear = ''
                    print(f'Movie year could not be pulled. Link: {movieLink}')

                # ADD MOVIE TO MOVIES LIST
                movies.append({
                    "rank": movie_rank,
                    "year": movieYear,
                    "name": movieName,
                    "link": movieLink
                })
                movie_rank += 1

            current_percentage = int(100 / _last_page_no) * (current_page_index + 1)
            if _last_page_no == current_page_index+1:
                if int(100 / _last_page_no) * _last_page_no != 100:
                    current_percentage = 100
    
            my_bar.progress(current_percentage, text=progress_text)
        except Exception as e:
            print(f'An error was encountered while obtaining movie information. Error: {e}')
    time.sleep(.2)
    my_bar.empty()
    return movies

def user_list_check(_dom, _url) -> tuple:
    try:
        if check_page_is_list(_dom):
            list_url = get_list_url(_dom)
            list_title = get_list_title(_dom)
            list_owner = get_list_owner(_dom)

            if not check_url_match(_url, list_url):
                # is redirected
                print(f'Redirected to {list_url}')

        context = {
            'list_url': list_url,
            'list_title': list_title,
            'list_owner': list_owner,
            'list_avaliable': True,
        }
    except Exception as e:
        print(f'An error occurred while checking the list. Error: {e}')
        context = {
            'list_avaliable': False
        }
    finally:
        return context

def get_meta_content(_dom, _obj) -> str:
    """
    a function that returns the content of the meta tag..
    """
    try:
        #> get the content of the meta tag.
        metaContent = _dom.find('meta', property=_obj).attrs['content']
    except AttributeError:
        #> if the meta tag is not found, return an empty string.
        print(f"Cannot retrieve '{_obj}' from the meta tag. Error Message: {AttributeError}")
        metaContent = ''
    return metaContent

def get_list_url(list_dom) -> str:
    list_url = get_meta_content(list_dom, 'og:url')
    return list_url

def get_list_title(list_dom) -> str:
    list_title = get_meta_content(list_dom, 'og:title')
    return list_title

def get_list_owner(list_dom) -> str:
    list_owner = get_body_content(list_dom, 'data-owner')
    return list_owner

# -- EDITOR FUNCTIONS --

def get_csv_syntax(movies) -> str:
    header = ['Year', 'Title', 'LetterboxdURI']
    csv_syntax = ','.join(header) + '\n'
    for movie in movies:
        csv_syntax += f'{movie["year"]},{movie["name"]},{movie["link"]}\n'
    return csv_syntax

# -- BOOL FUNCTIONS --

def check_url_match(url_1, url_2) -> bool:
    if url_1 == url_2 or f'{url_1}/' == url_2:
        return True
    return False

def check_page_is_list(_dom) -> bool:
    meta_content = get_meta_content(_dom,'og:type') 

    if meta_content == "letterboxd:list":
        print('Meta content confirmed that the entered address is a list.')
        print(f'Meta content: {meta_content}')
        return True
    else:
        print('This page not a list.')
        return False

def check_url_is_list(url) -> bool:
    site_url = 'https://letterboxd.com/'
    required_list = [site_url, '/list/']

    if all(x in url for x in required_list):
        print(f'URL: {url} is a list.')
        return True
    else:
        st.error(f'URL: {url} is not a list.')
        print(f'URL: {url} is not a list.')
        return False
    
def check_string_is_url(url) -> bool:
    try:
        requests.get(url)
        print(f'URL: {url} is a valid url.')
        return True
    except:
        st.error(f'URL: {url} is not a valid url.')
        print(f'URL: {url} is not a valid url.')
        return False

if __name__ == "__main__":
  st.title('Letterboxd List Downloader')
  url = st.text_input('Enter a list url')
  if url and check_string_is_url(url) and check_url_is_list(url):
    get_again = st.button('Get Again')

    list_dom = get_dom_from_url(url)

    checked_list = user_list_check(list_dom, url)
    list_avaliable = checked_list['list_avaliable']

    list_url = checked_list['list_url']
    list_title = checked_list['list_title']
    list_owner = checked_list['list_owner']
    list_domain_name = get_list_domain_name(list_url)
    list_movie_count = get_movie_count_from_meta_description(list_dom)

    list_detail_url = f'{list_url}detail/'
    list_detail_page_url = f'{list_detail_url}page/'
    
    list_detail_dom = get_dom_from_url(list_detail_url)
    last_page_no = get_list_last_page(list_detail_dom, list_detail_page_url)

    list_info_dict = {
        'list_url': list_url,
        'list_title': list_title,
        'list_owner': list_owner,
        'list_domain_name': list_domain_name,
        'last_page_no': last_page_no,
        'movies_count': list_movie_count
    }

    list_info = st.write(list_info_dict)

    # long process
    movies = get_movies_from_url(list_detail_page_url, last_page_no)

    if list_avaliable:
        # movies
        st.dataframe(pd.DataFrame(movies, columns=['rank', 'year', 'name', 'link']))
        csv_syntax = get_csv_syntax(movies)

        # download
        download_button = st.download_button(
            label="Download CSV",
            data=csv_syntax,
            file_name=f'{list_domain_name}.csv',
            mime='text/csv'
        )

        if download_button:
            st.success(f'{list_domain_name}.csv downloaded.')
    else:
        st.write('List is not avaliable.')
  else:
    st.write('Awaiting for URL to be entered.')

