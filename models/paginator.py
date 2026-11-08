"""
Shared resilient pagination and DOM fetching utilities for Letterboxd scrapers.

Provides exponential retry backoff, adaptive inter-page pacing, initial DOM reuse,
and real-time progress callback hooks.
"""

import time
from collections.abc import Callable

from letterboxdpy.core.exceptions import (
    AccessDeniedError,
    PrivateRouteError,
    ResourceNotFoundError,
)
from letterboxdpy.core.scraper import parse_url
from letterboxdpy.utils.utils_csv import transform_to_ranked_movies
from letterboxdpy.utils.utils_url import get_page_url

from models.logger import logger

MIN_PAGE_INTERVAL = 0.25


def pace_request(step_start: float, min_interval: float = MIN_PAGE_INTERVAL) -> None:
    """Ensure a minimum polite interval between network requests."""
    elapsed = time.monotonic() - step_start
    remaining = min_interval - elapsed
    if remaining > 0:
        time.sleep(remaining)


def fetch_dom_with_retry(url: str, retries: int = 3):
    """Fetch and parse page DOM with canonical trailing slash and retry backoff."""
    url = url if url.endswith("/") or "?" in url else f"{url}/"
    for attempt in range(retries):
        t0 = time.monotonic()
        try:
            dom = parse_url(url)
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            logger.info(
                "[FETCH] url=%s attempt=%d elapsed_ms=%d",
                url,
                attempt + 1,
                elapsed_ms,
            )
            return dom
        except (
            ResourceNotFoundError,
            PrivateRouteError,
            AccessDeniedError,
        ) as exc:
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            logger.warning(
                "[FETCH:ABORT] url=%s elapsed_ms=%d err=%s",
                url,
                elapsed_ms,
                exc,
            )
            break
        except Exception as exc:
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            logger.warning(
                "[FETCH:RETRY] url=%s attempt=%d/%d elapsed_ms=%d err=%s",
                url,
                attempt + 1,
                retries,
                elapsed_ms,
                exc,
            )
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
    max_pages: int | None = None,
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
        max_pages: Optional maximum number of pages to fetch.

    Returns:
        List of ranked movie dictionaries formatted for DataFrame display.
    """
    start_time = time.monotonic()
    collected = {}
    page = 1

    logger.info(
        "[PAGINATE:START] base_url=%s expected_total=%s items_per_page=%d cached_p1=%s max_pages=%s",
        base_url,
        total_count,
        items_per_page,
        initial_dom is not None,
        max_pages,
    )

    if total_count == 0:
        logger.info(
            "[PAGINATE:DONE] base_url=%s total_collected=0 pages=0 elapsed_ms=0",
            base_url,
        )
        return []

    while True:
        step_start = time.monotonic()
        used_cached = page == 1 and initial_dom is not None
        dom = (
            initial_dom
            if used_cached
            else fetch_dom_with_retry(get_page_url(base_url, page))
        )
        if not dom:
            break

        scraped = extractor_fn(dom)
        if not scraped:
            break

        prev_count = len(collected)
        collected.update(scraped)
        if len(collected) == prev_count:
            logger.warning(
                "[PAGINATE:STALLED] base_url=%s page=%d no new items added",
                base_url,
                page,
            )
            break

        logger.info(
            "[PAGINATE:PAGE] page=%d page_items=%d collected=%d/%s cached=%s",
            page,
            len(scraped),
            len(collected),
            total_count or "?",
            used_cached,
        )

        if on_progress is not None:
            on_progress(len(collected), total_count, page, items_per_page)

        if len(scraped) < items_per_page or (max_pages and page >= max_pages):
            break

        page += 1
        if not used_cached:
            pace_request(step_start)

    total_ms = int((time.monotonic() - start_time) * 1000)
    logger.info(
        "[PAGINATE:DONE] base_url=%s total_collected=%d pages=%d elapsed_ms=%d",
        base_url,
        len(collected),
        page,
        total_ms,
    )
    return transform_to_ranked_movies(collected)
