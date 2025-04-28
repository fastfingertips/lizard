import streamlit as st
from dataclasses import dataclass
from typing import Dict, Optional
import os

@dataclass
class PageConfig:
    page_title: str
    page_icon: str
    menu_items: Dict[str, str]

@dataclass
class BackgroundConfig:
    dark: str
    light: str

class Page:
    """Class managing page configuration and appearance"""
    
    def __init__(self):
        self.repo_slug = 'lizard'
        self._page_title = 'Letterboxd List Downloader'
        self._setup_page_config()
        self._setup_background()
        self._setup_styles()

    def _setup_page_config(self):
        """Sets up page configuration"""
        config = PageConfig(
            page_title=self._page_title,
            page_icon='🎬',
            menu_items={
                'Get Help': 'https://github.com/FastFingertips/lizard',
                'Report a bug': 'https://github.com/FastFingertips/lizard/issues',
                'About': 'This project is designed to download lists from Letterboxd. '
                        'The developer behind it is [@FastFingertips]'
                        '(https://github.com/FastFingertips).'
            }
        )
        st.set_page_config(**config.__dict__)

    def _setup_background(self):
        """Sets up background configuration"""
        background = BackgroundConfig(
            dark="""
            <style>
                .stApp {
                    background-image: linear-gradient(
                        180deg, 
                        #20272e, 
                        14%, 
                        #14181c, 
                        #14181c, 
                        #14181c
                    );
                }
            </style>
            """,
            light="""
            <style>
                .stApp {
                    background-image: linear-gradient(
                        180deg, 
                        #f2f2f2, 
                        14%, 
                        #e6e6e6, 
                        #e6e6e6, 
                        #e6e6e6
                    );
                }
            </style>
            """
        )
        st.markdown(background.dark, unsafe_allow_html=True)

    def _setup_styles(self):
        """Loads and applies external CSS styles"""
        css_file = os.path.join('static', 'styles', 'styles.css')
        with open(css_file, 'r') as f:
            css = f.read()
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    def create_title(self, text: Optional[str] = None):
        """Creates page title"""
        st.title(text or self._page_title)

    def create_footer(self):
        """Creates page footer"""
        html_file = os.path.join('static', 'templates', 'footer.html')
        with open(html_file, 'r') as f:
            html = f.read()
            st.markdown(html, unsafe_allow_html=True)
