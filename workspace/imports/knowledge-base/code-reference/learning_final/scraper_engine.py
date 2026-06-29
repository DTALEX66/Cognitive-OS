"""Backward-compatible wrapper: re-exports from scraper package"""
from .scraper import *
from .scraper.engine import UniversalScraper as ScraperEngine

class Platform:
    """Platform identifier for scraping operations."""
    def __init__(self, name: str = ""):
        self.name = name
    def __str__(self):
        return self.name
    def __repr__(self):
        return f"Platform({self.name!r})"

__all__ = ["ScraperEngine", "Platform"]
