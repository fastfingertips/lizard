from dataclasses import dataclass
from typing import Dict, Tuple
from typing_extensions import TypeAlias


Selector: TypeAlias = Tuple[str, Dict[str, str]]

@dataclass
class FilmSelectors:
    """Selectors for film list elements"""
    # <div class="list-detailed-entries-list js-list-entries">
    LIST: Selector = ('div', {'class': 'js-list-entries'})
    # <h2 class="primaryname">
    HEADLINE: Selector = ('h2', {'class': 'primaryname'})

@dataclass
class MetaSelectors:
    """Selectors for meta elements"""
    DESCRIPTION: Selector = ('meta', {'name': 'description'})

@dataclass
class PageSelectors:
    """Selectors for page elements"""
    ERROR_BODY: Selector = ('body', {'class': 'error'})
    ERROR_MESSAGE: Selector = ('section', {'class': 'message'})
    LAST_PAGE: Selector = ('div', {'class': 'paginate-pages'})
    ARTICLES: Selector = ('ul', {'class': 'poster-list -p70 film-list clear film-details-list'}) 