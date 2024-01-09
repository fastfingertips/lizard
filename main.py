from bs4 import BeautifulSoup as TagSoup
import streamlit as st
import pandas as pd
import requests
import validators
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

class Url():

    def __init__(self, url, url_dom=None):
        self.url = url
        self.detail_url = url + 'detail/'
        self.page_url = self.detail_url + 'page/'

        self.slug = ''

        self.url_dom = url_dom if url_dom else get_dom_from_url(self.url)
        self.detail_url_dom = get_dom_from_url(self.detail_url)

class MovieList(Url):
    
        def __init__(self, url):
            super().__init__(url.url, url.url_dom)
            self.title = ''
            self.owner = ''
            self.last_page = 0
            self.movie_count = 0

        def get_movies(self, last_page) -> list:
            progress_text = 'Getting movies from list..'
            self.url += 'detail/' + 'page/' # detail and page slug
            my_bar = st.progress(0, text=progress_text)
            movie_rank = 1
            movies = []

            for current_page_index in range(int(last_page)):
                list_current_page_url = self.url + str(current_page_index + 1) # .../list/.../detail/page/1
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

                    # fix the last percentage
                    current_percentage = int(100 / last_page) * (current_page_index + 1)
                    if last_page == current_page_index+1:
                        if int(100 / last_page) * last_page != 100:
                            current_percentage = 100
            
                    my_bar.progress(current_percentage, text=progress_text)
                except Exception as e:
                    print(f'An error was encountered while obtaining movie information. Error: {e}')
            time.sleep(.2)
            my_bar.empty()
            return movies
  

class UrlManager:

        def check_url_match(url_1, url_2) -> bool:
            if url_1 == url_2 or f'{url_1}/' == url_2:
                return True
            return False

        def check_string_is_url(url) -> bool:
            """
            this function checks url is valid or not,
            and returns bool value as result.
            """
            return validators.url(url)

        def check_url_pattern(url) -> bool:
            """
            this function checks url is list or not,
            and returns bool value as result.
            """
            site_url = 'https://letterboxd.com/'
            required_path = '/list/'
    
            if all(x in url for x in [site_url, required_path]):
                return True
            else:
                return False
            
        def get_list_domain_name(_url) -> str:
            return _url[_url.index('/list/')+len('/list/'):].replace('/','')

class Checker:

    def __init__(self, dom):
        self.dom = dom
        self.dom_parser = DomParser(dom)

    def check_page_is_list(self) -> bool:
        """
        this function checks dom's meta tag,
        og:type is letterboxd:list or not,
        and returns bool value as result.
        """

        meta_content = self.dom_parser.get_meta_content('og:type')

        context = {
            'is_list': meta_content == 'letterboxd:list',
            'meta_content': meta_content
            }
        return context
    
    def user_list_check(self, url) -> dict:
        try:
            current_list = ListPage(self.dom)
            list_url = current_list.get_list_url()
            list_title = current_list.get_list_title()
            list_owner = current_list.get_list_owner()

            if not UrlManager.check_url_match(url, list_url):
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

class DomParser:

    def __init__(self, dom):
        self.dom = dom

    def get_meta_content(self, _obj) -> str:
        """
        a function that returns the content of the meta tag..
        """
        try:
            #> get the content of the meta tag.
            metaContent = self.dom.find('meta', property=_obj).attrs['content']
        except AttributeError:
            #> if the meta tag is not found, return an empty string.
            print(f"Cannot retrieve '{_obj}' from the meta tag. Error Message: {AttributeError}")
            metaContent = None
        return metaContent

    def get_body_content(self, _obj) -> str:
        """
        a function that returns the content of the body tag..
        """
        #> get the content of the body tag.
        bodyContent = self.dom.find('body').attrs[_obj]
        return bodyContent

    def get_movie_count_from_meta(self) -> int:
        print('Getting the number of movies on the list meta description.')
        # Instead of connecting to the last page and getting the number of movies on the last page, which generates a GET request
        # and slows down the program, an alternative approach is used by getting the meta description of the list page.
        metaDescription = self.dom.find(*paths['meta_description']).attrs['content']
        metaDescription = metaDescription[10:] # after 'A list of' in the description

        for i in range(6):
            try:
                int(metaDescription[i])
                ii = i+1
            except: pass
        movie_count = metaDescription[:ii]
        return movie_count

    def get_list_last_page(self, url) -> int:
        """
        Get the number of pages in the list (last page no)
        """
        url += 'detail/' + 'page/' # detail and page slug
        try:
            # note: To find the number of pages, count the li's. Take the last number.
            # the text of the link in the last 'li' will give us how many pages our list is.
            print('Checking the number of pages in the list..')
            # not created link when the number of movies is 100 or less in the list.
            last_page_no = self.dom.find(*paths['last_page_no']).find_all("li")[-1].a.text 
            print(f'The list has more than one page ({last_page_no}).')
        except AttributeError: # exception when there is only one page.
            print('There is no more than one page, this list is one page.')
            last_page_no = 1 # when the number of pages cannot be obtained, the number of pages is marked as 1.
            print(last_page_no, self.dom, url) # send page info.
        except Exception as e:
            print(f'An error occurred while checking the number of pages in the list. Error: {e}')
        finally:
            print(f'Communication with the page is complete. It is learned that the number of pages in the list is {last_page_no}.')
            return int(last_page_no)

class ListPage:

    def __init__(self, dom):
        self.dom_parser = DomParser(dom)

    def get_list_url(self) -> str:
        list_url = self.dom_parser.get_meta_content('og:url')
        return list_url

    def get_list_title(self) -> str:
        list_title = self.dom_parser.get_meta_content('og:title')
        return list_title

    def get_list_owner(self) -> str:
        list_owner = self.dom_parser.get_body_content('data-owner')
        return list_owner

# -- EDITOR FUNCTIONS --

def get_csv_syntax(movies) -> str:
    header = ['Year', 'Title', 'LetterboxdURI']
    csv_syntax = ','.join(header) + '\n'
    for movie in movies:
        csv_syntax += f'{movie["year"]},{movie["name"]},{movie["link"]}\n'
    return csv_syntax

def set_page_style():
    st.markdown(
        """
        <style>
            .stApp {
                background-image: linear-gradient(180deg, #20272e, 14%, #14181c, #14181c, #14181c);
            }
        </style>
        """,
        unsafe_allow_html=True
    )

def init_page_config():
    st.set_page_config(
        page_title='Letterboxd List Downloader',
        page_icon='🎬',
        menu_items={
            'Get Help': 'https://github.com/FastFingertips/streamlit-letterboxd-downloader',
            'Report a bug': 'https://github.com/FastFingertips/streamlit-letterboxd-downloader/issues',
            'About': 'This project is designed to download lists from Letterboxd. The developer behind it is [@FastFingertips](https://github.com/FastFingertips).'
        }
    )

if __name__ == "__main__":
    # Page Config
    init_page_config()

    # Page Style
    set_page_style()

    st.title('Letterboxd List Downloader')
    url_params = st.experimental_get_query_params()

    textbox_placeholder = 'Enter a list **url** or **username/list-title**'
    if url_params and 'q' in url_params:
        # print('URL Params Found')
        user_input = url_params['q'][0]
        user_input = st.text_input(textbox_placeholder, value=user_input)
    else:
        # print('URL Params Not Found')
        user_input = st.text_input(textbox_placeholder)

    if user_input.strip():
        input_is_url = UrlManager.check_string_is_url(user_input)

        # check if user_input is url
        if not input_is_url:
            # check if user_input is username/list-title
            if '/' in user_input:
                # use list if user input is username/list-title
                username, list_title = user_input.split('/', 1) # maxsplit=1
                # check if username and list_title is not empty
                if all([username, list_title]):
                    user_input = f'https://letterboxd.com/{username}/list/{list_title}/'

        # check if pattern is valid
        if UrlManager.check_url_pattern(user_input):
            get_again = st.button('Get Again')
            list_dom = get_dom_from_url(user_input)

            # create checker object for page
            checker = Checker(list_dom)

            # check if page is list
            list_meta_verify = checker.check_page_is_list()
            if list_meta_verify['is_list']:
                checked_list = checker.user_list_check(user_input)

                movie_list = MovieList(
                    Url(checked_list['list_url'], list_dom)
                )

                list_details = {}

                # objects
                list_dom_parser = DomParser(movie_list.url_dom)
                list_detail_dom_parser = DomParser(movie_list.detail_url_dom)

                # list info
                movie_list.title = checked_list['list_title']
                movie_list.owner = checked_list['list_owner']
                movie_list.slug = UrlManager.get_list_domain_name(movie_list.url)
                movie_list.last_page = list_detail_dom_parser.get_list_last_page(movie_list.url)
                movie_list.movie_count = list_dom_parser.get_movie_count_from_meta()

                # print list info
                for key, value in movie_list.__dict__.items():
                    list_details[key] = '🚫' if 'dom' in key else value
                json_info = st.json(list_details, expanded=False)

                # "since this process may take a long time, we print the list information on the screen before.
                # this way we can see which list is downloaded."
                movies = movie_list.get_movies(movie_list.last_page)


                if checked_list['list_avaliable']:
                    st.dataframe(
                        pd.DataFrame(
                            movies,
                            columns=["rank", "year", "name", "link"]
                        ),
                        hide_index=True,
                        use_container_width=True,
                    )

                    # Download process
                    csv_data = get_csv_syntax(movies)
                    download_filename = movie_list.slug + '.csv'
                    download_button = st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=download_filename,
                        mime='text/csv'
                    )

                    if download_button: st.success(f'{download_filename} downloaded.')
            else:
                err_msg = list_dom.find('body', class_='error')
                err_msg = list_dom.find('section', class_='message').p.get_text()
                err_msg = err_msg.split('\n')
                err_msg = err_msg[0].strip()
                st.error(f'{err_msg}', icon='👀')
        else: st.warning('Please enter a valid **list url** or **username/list-title.**', icon='💡')
    else: st.write('_Awaiting input.._')
