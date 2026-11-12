"""
Structured telemetry and performance logger for Lizard.

Writes millisecond-precision execution, pagination, and cache events to
both standard output and `logs/lizard.log` for real-time diagnostics.
"""

import logging
import os
import sys
import time
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "lizard.log")


def get_logger(name: str = "lizard") -> logging.Logger:
    """Return a configured singleton logger instance."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d | %(levelname)-5s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=2, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        pass

    return logger


logger = get_logger()


@contextmanager
def log_step(tag: str, **meta):
    """Context manager to log operation duration in milliseconds."""
    meta_str = " ".join(f"{k}={v}" for k, v in meta.items() if v is not None)
    start = time.monotonic()
    logger.info("[%s:START] %s", tag, meta_str)
    try:
        yield
    except Exception as exc:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        log_fn = (
            logger.warning
            if exc.__class__.__name__ == "ResourceNotFoundError"
            else logger.error
        )
        log_fn(
            "[%s:%s] %s elapsed_ms=%d err=%s",
            tag,
            "WARN" if exc.__class__.__name__ == "ResourceNotFoundError" else "ERROR",
            meta_str,
            elapsed_ms,
            exc,
        )
        raise
    else:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.info("[%s:DONE] %s elapsed_ms=%d", tag, meta_str, elapsed_ms)
