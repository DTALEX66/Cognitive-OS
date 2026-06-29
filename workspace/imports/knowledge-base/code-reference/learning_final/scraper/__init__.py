"""Universal Scraper System - Any Platform, Any Website, Any Company"""
from __future__ import annotations
from .engine import UniversalScraper
from .router import PlatformRouter
from .registry import PLATFORM_REGISTRY, PlatformConfig, detect_platform, list_platforms
from .strategies import StrategyChain, StrategyResult, StrategyType
from .strategies import HTTPStrategy, CurlCFFIStrategy, HttpxStrategy, PlaywrightStrategy
from .strategies import MarkdownifyStrategy, ArchiveStrategy, RSSStrategy
from .extractors import PlatformExtractors, TextExtractor, get_extractor
from .cache import CacheLayer
from .fingerprints import Fingerprint, FingerprintManager
from .proxies import ProxyManager
from .antibots import AntiBotDetector, CookieManager
__all__ = [
    "UniversalScraper", "PlatformRouter", "PLATFORM_REGISTRY", "PlatformConfig",
    "detect_platform", "list_platforms",
    "StrategyChain", "StrategyResult", "StrategyType",
    "HTTPStrategy", "CurlCFFIStrategy", "HttpxStrategy", "PlaywrightStrategy",
    "MarkdownifyStrategy", "ArchiveStrategy", "RSSStrategy",
    "PlatformExtractors", "TextExtractor", "get_extractor",
    "CacheLayer", "Fingerprint", "FingerprintManager",
    "ProxyManager", "AntiBotDetector", "CookieManager",
]
