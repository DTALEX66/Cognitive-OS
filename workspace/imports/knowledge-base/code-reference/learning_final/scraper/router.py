"""URL Router - Auto-detect platform from any URL"""
from __future__ import annotations
from .registry import detect_platform, PLATFORM_REGISTRY
from .extractors import TextExtractor, get_extractor
from .cache import CacheLayer

class PlatformRouter:
    def __init__(self, cache=None):
        self._cache = cache

    def route(self, url):
        return detect_platform(url)

    def extract(self, html_text, platform=""):
        te = TextExtractor()
        data = {
            "title": te.extract_title(html_text) or "",
            "text": te.extract_text(html_text) or "",
            "description": te.extract_description(html_text) or "",
            "author": te.extract_author(html_text) or "",
            "published": te.extract_publish_date(html_text) or "",
            "meta": te.extract_meta_tags(html_text),
            "links": te.extract_links(html_text),
            "images": te.extract_images(html_text),
            "json_ld": te.extract_json_ld(html_text),
            "content_type": "webpage",
        }
        try:
            extractor = get_extractor(platform)
            result = extractor(data)
            data.update(result)
        except: pass
        return data

    def normalize_to_card(self, data, platform, url):
        extractor = get_extractor(platform)
        card = extractor(data)
        card.update({
            "tags": card.get("tags", platform) + "," + platform,
            "source_url": url,
            "source_type": card.get("source_type", "webpage"),
            "platform": platform,
        })
        return card
