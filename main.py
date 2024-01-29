from bs4 import BeautifulSoup as TagSoup
from models.parser import DomParser
from paths import paths
import streamlit as st
import pandas as pd
import validators
import requests
import time
import json

class Notifier:

    link = "https://ntfy.sh/"
    encoding = 'utf-8'

    def __init__(self):
        pass

    @classmethod
    def link_update(cls, code):
        raw = f'https://rentry.co/{code}/raw'
        data = requests.get(raw)
        cls.link += json.loads(data.content)['log_id']
        print(f"Log link updated: '{cls.link}'.")

    def send(self, message):
        requests.post(
            self.link,
            data=message.encode(encoding=self.encoding)
            )

class Url():

    domain_name = 'https://letterboxd.com/'

    def __init__(self, url, url_dom=None):
        
        self.url = url
        self.detail_url = url + 'detail/'
        self.page_url = self.detail_url + 'page/'

        self._url_dom = url_dom
        self._detail_url_dom = None

        self.slug = UrlManager.get_list_domain_name(self.url)

        self._dom_parser = None
        self._detail_dom_parser = None

    @property
    def url_dom(self):
        if not self._url_dom:
            self._url_dom = get_dom_from_url(self.url)
            self._dom_parser = DomParser(self.url_dom)
        return self._url_dom
    
    @property
    def detail_url_dom(self):
        if not self._detail_url_dom:
            self._detail_url_dom = get_dom_from_url(self.detail_url)
            self._detail_dom_parser = DomParser(self._detail_url_dom)
        return self._detail_url_dom
    
    @property
    def dom_parser(self):
        if not self._dom_parser:
            self._dom_parser = DomParser(self.url_dom)
        return self._dom_parser
    
    @property
    def detail_dom_parser(self):
        if not self._detail_dom_parser:
            self._detail_dom_parser = DomParser(self.detail_url_dom)
        return self._detail_dom_parser

class MovieList(Url):

        def __init__(self, url):
            super().__init__(url.url, url.url_dom)
            self._short_url = None
            self.title = self.get_list_title()
            self.owner = self.get_list_owner()
            self._movies = [] 
            self.last_page = self.detail_dom_parser.get_list_last_page()
            self.movie_count = self.dom_parser.get_movie_count_from_meta()

        def get_movies(self, caching = False) -> list:
            print('Fetching movies from list..')
            if caching:
                progress_text = 'Getting movies from list..'
                my_bar = st.progress(0, text=progress_text)
            movie_rank = 1

            for current_page_index in range(int(self.last_page)):
                list_current_page_url = self.page_url + str(current_page_index + 1) # .../list/.../detail/page/1

                if current_page_index:
                    current_page_dom = get_dom_from_url(list_current_page_url)
                else:
                    # if current page is first page, use already pulled dom
                    if self.detail_url_dom is not None:
                        current_page_dom = self.detail_url_dom

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
                            print(f'Movie year could not be pulled. Check link: {movieLink}')

                        # ADD MOVIE TO MOVIES LIST
                        self._movies.append({
                            "rank": movie_rank,
                            "year": movieYear,
                            "name": movieName,
                            "link": movieLink
                        })
                        movie_rank += 1
                    if caching:
                        # fix the last percentage
                        current_percentage = int(100 / self.last_page) * (current_page_index + 1)
                        if self.last_page == current_page_index+1:
                            if int(100 / self.last_page) * self.last_page != 100:
                                current_percentage = 100
                
                        my_bar.progress(current_percentage, text=progress_text)
                except Exception as e:
                    print(f'An error was encountered while obtaining movie information. Error: {e}')
            time.sleep(.4)
            if caching:
                my_bar.empty()
            return self._movies

        @property
        def short_url(self):
            """
            this function checks short_url is avaliable or not,
            and returns short_url as result.
            """
            if self._short_url:
                return self._short_url
            else:
                self._short_url = self.dom_parser.get_list_short_url()
                return self._short_url

        @property
        def movies(_self):
            """
            this function checks movies is avaliable or not,
            and returns movies as result.
            """
            if _self._movies:
                return _self._movies
            else:
                _self._movies = _self.get_movies()
                return _self._movies

        def get_list_url(self) -> str:
            list_url = self.dom_parser.get_meta_content('og:url')
            return list_url

        def get_list_title(self) -> str:
            list_title = self.dom_parser.get_meta_content('og:title')
            return list_title

        def get_list_owner(self) -> str:
            list_owner = self.dom_parser.get_body_content('data-owner')
            return list_owner

class UrlManager:

    @staticmethod
    def check_url_match(url_1, url_2) -> bool:
        if url_1 == url_2 or f'{url_1}/' == url_2:
            return True
        return False

    @staticmethod
    def check_string_is_url(url) -> bool:
        """
        this function checks if the URL is valid or not,
        and returns a boolean value as the result.
        """
        return validators.url(url)

    @staticmethod
    def check_url_pattern(url) -> bool:
        """
        this function checks if the URL is a list or not,
        and returns a boolean value as the result.
        """

        matches = ['://letterboxd', '://boxd.it']
        protocols = ['http', 'https']
        
        for match in matches:
            if match in url:
                match_index = url.index(match)
                protocol = url[:match_index]
                if protocol in protocols:
                    print(f'URL pattern is valid. ({protocol})')
                    return True
        return False

    @staticmethod
    def get_list_domain_name(url) -> str:
        return url[url.index('/list/') + len('/list/'):].replace('/', '')

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
            list_url = self.dom_parser.get_meta_content('og:url')
            list_title = self.dom_parser.get_meta_content('og:title')
            list_owner = self.dom_parser.get_body_content('data-owner')

            if not UrlManager.check_url_match(url, list_url):
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

class InputManager:
    textbox_placeholder = 'Enter a list **url** or **username/list-title**.'

    def __init__(self):
        self.data = {
            'input': st.text_input(label=self.textbox_placeholder),
            'query': st.experimental_get_query_params()
        }

    def process_data(self):
        input_data = self.data['input']
        query_data = self.data['query']

        if input_data:
            data = input_data
        elif 'q' in query_data:
            # URL Params Found
            data = query_data['q'][0]
        else:
            data = None

        return data.strip() if data else None

    @staticmethod
    def check_and_format_url(data):
        """
        normal:
            fastfingertips/list_name                              -> fastfingertips/list_name
            fastfingertips/list/list_name                         -> fastfingertips/list_name
            fastfingertips/list/list_name/detail                  -> fastfingertips/list_name

        specific names('list' or 'detail'):
            # if a list's name is 'list'?
            `fastfingertips/list`                                 -> fastfingertips/list
            `fastfingertips/list/list`                            -> fastfingertips/list
            `fastfingertips/list/list/detail`                     -> fastfingertips/list

            # if a list's name is 'detail'?
            `fastfingertips/detail`                               -> fastfingertips/detail
            `fastfingertips/detail/detail`                        -> fastfingertips/detail
            `fastfingertips/list/detail`                          -> fastfingertips/detail
            `fastfingertips/list/detail/detail`                   -> fastfingertips/detail

        filters:
            `fastfingertips/list_name/decade/1990s/genre/crime+-comedy/by/popular`
            `fastfingertips/list/list_name/decade/1990s/genre/crime+-comedy/by/popular`
            `fastfingertips/list/list_name/detail/decade/1990s/genre/crime+-comedy/by/popular`

        extras: 
            checks the / sign at the end and beginning of the data.
        """
        if '/' in data:

            # 1. remove '/' from start and end of string
            if len(data) <= 2:
                print('Error: Data is too short.')
                return None

            if data[0] == '/': data = data[1:]
            if data[-1] == '/': data = data[:-1]
                
            # 2. split data by '/'
            if '/' not in data:
                print('Error: Data does not contain a / character.')
                return None

            data_blocks = data.split('/')
            username = data_blocks[0]
            data_blocks = data_blocks[1:] 

            if len(data_blocks) == 1:
                list_slug = data_blocks[0]
                data_blocks.clear()
            else:
                if data_blocks[0] == 'list':

                    if data_blocks[1] == 'list':
                        list_slug = data_blocks[1]
                        data_blocks = data_blocks[2:]
                        if data_blocks:
                            if data_blocks[0] == 'detail':
                                # /list/list/detail
                                data_blocks = data_blocks[1:]

                    elif data_blocks[1] == 'detail':
                        list_slug = data_blocks[1]
                        data_blocks = data_blocks[2:]
                        if data_blocks:
                            if data_blocks[0] == 'detail':
                                # /list/detail/detail
                                data_blocks = data_blocks[1:]

                    else:
                        # list/list_name
                        list_slug = data_blocks[1]
                        data_blocks = data_blocks[2:]
                        if data_blocks:
                            # list/list_name/?
                            if data_blocks[0] == 'detail':
                                # list/list_name/detail
                                data_blocks = data_blocks[1:]

                elif data_blocks[0] == 'detail':
                    if data_blocks[1] == 'detail':
                        list_slug = data_blocks[0]
                        data_blocks = data_blocks[2:]
                    else:
                        list_slug = data_blocks[0]
                        data_blocks = data_blocks[1:]
                        pass
                else:
                    list_slug = data_blocks[0]
                    data_blocks = data_blocks[1:]
                    pass

            print(f'List name: {list_slug}')
            print(f'Username: {username}')
            print(f'Blocks: {data_blocks}')

            try:
                if all([username, list_slug]):
                    filters = ''
                    if data_blocks:
                        filters = '/'.join(data_blocks)
                    return f'https://letterboxd.com/{username}/list/{list_slug}/' + filters
                else:
                    print('Error: Username or list title is empty.')
            except Exception as e:
                print(f'Error: {e}')
                pass
        else:
            # FUTURE: operations entered with only username or list name
            print('Error: Data does not contain a / character.')

        return None

class Page:
    config = {
        'page_config':{ 
            'page_title':'Letterboxd List Downloader',
            'page_icon':'🎬',
            'menu_items':{
            'Get Help': 'https://github.com/FastFingertips/streamlit-letterboxd-downloader',
            'Report a bug': 'https://github.com/FastFingertips/streamlit-letterboxd-downloader/issues',
            'About': 'This project is designed to download lists from Letterboxd. The developer behind it is [@FastFingertips](https://github.com/FastFingertips).'
            }
        },
        'background': {
            'dark':
            """
            <style>
                .stApp {
                    background-image: linear-gradient(180deg, #20272e, 14%, #14181c, #14181c, #14181c);
                }
            </style>
            """,
            'light':
            """
            <style>
                .stApp {
                    background-image: linear-gradient(180deg, #f2f2f2, 14%, #e6e6e6, #e6e6e6, #e6e6e6);
                }
            </style>
            """
        }
    }

    st.set_page_config(**config['page_config'])
    st.markdown(config['background']['dark'], unsafe_allow_html=True)

    def __init__(self):
        pass

    def create_title(self, text:str=None):
        if text is None:
            text = self.config['page_config']['page_title']
        st.title(text)

def get_dom_from_url(_url) -> TagSoup:
    """
    Reads and retrieves the DOM of the specified page URL.
    """
    try:
        #> Provides information in the log file at the beginning of the connection.
        print(f'Conection to the address [{_url}] is being established..')
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

def get_csv_syntax(movies) -> str:
    # https://letterboxd.com/about/importing-data/
    # https://letterboxd.com/list/new/
    header = ['Year', 'Title', 'LetterboxdURI']
    csv_syntax = ','.join(header) + '\n'
    for movie in movies:
        csv_syntax += f'{movie["year"]},{movie["name"]},{movie["link"]}\n'
    return csv_syntax

if __name__ == "__main__":
    # Render
    page = Page()
    page.create_title()

    # Input
    input_manager = InputManager()
    data = input_manager.process_data()

    notifier = Notifier()
    notifier.link_update('dynamic_data')

    # Process data
    if data:
        input_is_url = UrlManager.check_string_is_url(data)

        if not input_is_url:
            # data is not url, so we check if it is username/list-title
            data = input_manager.check_and_format_url(data)

        if data:
            # create checker object for page
            is_letterboxd_list = UrlManager.check_url_pattern(data)
            url_dom = get_dom_from_url(data)
            checker = Checker(url_dom)
            list_meta_verify = checker.check_page_is_list()

            btn_get_again = st.button('Get Again')

            if list_meta_verify['is_list']:
                # send notification
                notifier.send(f'List downloaded: {data}')

                # create checker object for list
                checked_list = checker.user_list_check(data)

                # address is list, so we can create the object now
                movie_list = MovieList(
                    Url(
                        checked_list['list_url'],
                        url_dom
                    )
                )

                print(f'List short url: {movie_list.short_url}')
                # print list info
                list_details = {}
                for key, value in movie_list.__dict__.items():
                    list_details[key] = '🚫' if 'dom' in key else value
                json_info = st.json(list_details, expanded=False)

                # "since this process may take a long time, we print the list information on the screen before.
                # this way we can see which list is downloaded."

                if checked_list['list_avaliable']:
                    st.dataframe(
                        pd.DataFrame(
                            movie_list.movies,
                            columns=["rank", "year", "name", "link"]
                        ),
                        hide_index=True,
                        use_container_width=True,
                    )

                    # Download process
                    csv_data = get_csv_syntax(movie_list.movies)
                    download_filename = movie_list.slug + '.csv'
                    download_button = st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=download_filename,
                        mime='text/csv'
                    )

                    if download_button: st.success(f'{download_filename} downloaded.')
            elif url_dom.find('body', class_='error'):
                err_msg = url_dom.find('body', class_='error')
                err_msg = url_dom.find('section', class_='message').p.get_text()
                err_msg = err_msg.split('\n')
                err_msg = err_msg[0].strip()
                st.error(f'{err_msg}', icon='👀')
            else:
                st.warning('Please enter a valid **list url** or **username/list-title.**', icon='💡')
        else:
            st.warning('**username/list-title.**', icon='💡')
    else:
        st.write('_Awaiting input.._')
