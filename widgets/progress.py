"""
Modular stqdm-style progress tracker widget for Streamlit.

Provides real-time progress bars, item/page counters, speed (items/s),
and ETA metrics during multi-page scraping operations.
"""

import math
import time

import streamlit as st


class ProgressTracker:
    """Context manager and callback handler for stqdm-style progress display."""

    def __init__(
        self,
        desc: str = "Loading",
        total: int | None = None,
        unit: str = "movies",
        leave: bool = False,
    ):
        self.desc = desc
        self.total = total if (total and total > 0) else None
        self.unit = unit
        self.leave = leave
        self.start_time = 0.0
        self._placeholder = None
        self._bar = None
        self._caption = None

    def __enter__(self):
        self.start_time = time.monotonic()
        self._placeholder = st.empty()
        with self._placeholder.container():
            self._bar = st.progress(0.0)
            self._caption = st.empty()
            self._render_status(0, self.total, 1, None)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.leave and self._placeholder is not None:
            self._placeholder.empty()

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds as MM:SS."""
        seconds = max(0, int(seconds))
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def _render_status(
        self,
        current: int,
        total: int | None,
        page: int | None,
        items_per_page: int | None,
    ):
        elapsed = max(0.001, time.monotonic() - self.start_time)
        rate = current / elapsed if (current > 0 and elapsed >= 0.15) else 0.0
        rate_str = f"{rate:.1f} {self.unit}/s" if rate > 0 else f"-- {self.unit}/s"
        elapsed_str = self._format_time(elapsed)

        if total and total > 0:
            effective_total = max(current, total)
            ratio = min(1.0, current / effective_total)
            pct = int(ratio * 100)
            remaining = (effective_total - current) / rate if rate > 0 else 0.0
            eta_str = self._format_time(remaining) if rate > 0 else "--:--"
            page_info = ""
            if page and items_per_page:
                total_pages = max(page, math.ceil(effective_total / items_per_page))
                page_info = f" • Page {page}/{total_pages}"
            status = (
                f"**{self.desc}** — `{current}/{effective_total}` {self.unit} ({pct}%)"
                f"{page_info} • `[{elapsed_str}<{eta_str}, {rate_str}]`"
            )
        else:
            ratio = (
                min(0.95, 1.0 - (1.0 / (1.0 + (page or 1) * 0.5)))
                if current > 0
                else 0.0
            )
            page_info = f" • Page {page}" if page else ""
            status = (
                f"**{self.desc}** — `{current}` {self.unit}"
                f"{page_info} • `[{elapsed_str}, {rate_str}]`"
            )

        if self._bar is not None:
            self._bar.progress(ratio)
        if self._caption is not None:
            self._caption.markdown(status)

    def update(
        self,
        current: int,
        total: int | None = None,
        page: int | None = None,
        items_per_page: int | None = None,
    ):
        """Update progress bar and telemetry metrics."""
        resolved_total = total if (total and total > 0) else self.total
        self._render_status(current, resolved_total, page, items_per_page)
