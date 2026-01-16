"""Crawlers package for collecting bank review data from various platforms."""

from .applestore import crawl_apple_store
from .googleplay import crawl_google_play
from .facebook import crawl_facebook

__all__ = [
    "crawl_apple_store",
    "crawl_google_play", 
    "crawl_facebook"
]
