"""
Shared resilient pagination and DOM fetching utilities for Letterboxd scrapers.

Provides exponential retry backoff, polite inter-page pacing, initial DOM reuse,
and real-time progress callback hooks.
"""

import time
from collections.abc import Callable

from letterboxdpy.core.scraper import parse_url
from letterboxdpy.utils.utils_csv import transform_to_ranked_movies
from letterboxdpy.utils.utils_url import get_page_url


def fetch_dom_with_retry(url: str, retries: int = 3):
    """Fetch and parse page DOM with exponential retry backoff."""
    for attempt in range(retries):
        try:
            return parse_url(url)
        except Exception:
            if attempt == retries - 1:
                break
            time.sleep(1.0 * (attempt + 1))
    return None


def paginate_ranked_movies(
    base_url: str,
    items_per_page: int,
    extractor_fn: Callable,
    initial_dom=None,
    total_count: int | None = None,
    on_progress: Callable | None = None,
) -> list:
    """
    Scrape paginated Letterboxd movie collections with progress reporting.

    Args:
        base_url: Base collection URL to paginate.
        items_per_page: Maximum number of items expected per full page.
        extractor_fn: Function taking a BeautifulSoup DOM and returning a dict of movies.
        initial_dom: Optional pre-fetched DOM for page 1 to avoid duplicate requests.
        total_count: Expected total movie count for progress percentage calculation.
        on_progress: Optional callback(current, total, page, items_per_page).

    Returns:
        List of ranked movie dictionaries formatted for DataFrame display.
    """
    collected = {}
    page = 1

    while True:
        dom = (
            initial_dom
            if (page == 1 and initial_dom is not None)
            else fetch_dom_with_retry(get_page_url(base_url, page))
        )
        if not dom:
            break

        scraped = extractor_fn(dom)
        if not scraped:
            break

        collected.update(scraped)

        if on_progress is not None:
            on_progress(len(collected), total_count, page, items_per_page)

        if len(scraped) < items_per_page:
            break

        page += 1
        time.sleep(0.5)

    return transform_to_ranked_movies(collected)
