from dataclasses import dataclass
from typing import Dict, Tuple, TypeAlias

Selector: TypeAlias = Tuple[str, Dict[str, str]]

@dataclass
class FilmSelectors:
    """Selectors for film list elements"""
    LIST: Selector = ('ul', {'class': 'js-list-entries poster-list -p70 film-list clear film-details-list'})
    HEADLINE: Selector = ('h2', {'class': 'headline-2 prettify'})

@dataclass
class MetaSelectors:
    """Selectors for meta elements"""
    DESCRIPTION: Selector = ('meta', {'name': 'description'})

@dataclass
class PageSelectors:
    """Selectors for page elements"""
    LAST_PAGE: Selector = ('div', {'class': 'paginate-pages'})
    ARTICLES: Selector = ('ul', {'class': 'poster-list -p70 film-list clear film-details-list'}) 