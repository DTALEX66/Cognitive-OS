"""Content Extractors - Platform-specific and generic extraction"""
from __future__ import annotations
from typing import Any, Optional, Callable
import json, re as re_mod, html

class TextExtractor:
    @staticmethod
    def extract_title(html_text):
        m = re_mod.search(r"<title[^>]*>([^<]+)</title>", html_text, re_mod.IGNORECASE | re_mod.DOTALL)
        if m: return html.unescape(m.group(1)).strip()
        m = re_mod.search(r"<h1[^>]*>([^<]+)</h1>", html_text, re_mod.IGNORECASE | re_mod.DOTALL)
        if m: return html.unescape(m.group(1)).strip()
        m = re_mod.search(r"<meta[^>]+property=[\"']og:title[\"'][^>]+content=[\"']([^\"']+)[\"']", html_text, re_mod.IGNORECASE)
        if m: return html.unescape(m.group(1)).strip()
        return ""

    @staticmethod
    def extract_description(html_text):
        m = re_mod.search(r"<meta[^>]+name=[\"']description[\"'][^>]+content=[\"']([^\"']+)[\"']", html_text, re_mod.IGNORECASE)
        if m: return html.unescape(m.group(1)).strip()
        m = re_mod.search(r"<meta[^>]+property=[\"']og:description[\"'][^>]+content=[\"']([^\"']+)[\"']", html_text, re_mod.IGNORECASE)
        if m: return html.unescape(m.group(1)).strip()
        return ""

    @staticmethod
    def extract_text(html_text):
        text = re_mod.sub(r"<script[^>]*>.*?</script>", "", html_text, flags=re_mod.DOTALL | re_mod.IGNORECASE)
        text = re_mod.sub(r"<style[^>]*>.*?</style>", "", text, flags=re_mod.DOTALL | re_mod.IGNORECASE)
        text = re_mod.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        text = re_mod.sub(r"\s+", " ", text).strip()
        return text[:100000]

    @staticmethod
    def extract_json_ld(html_text):
        results = []
        for m in re_mod.finditer(r"<script[^>]+type=[\"']application/ld\\+json[\"'][^>]*>(.*?)</script>", html_text, re_mod.DOTALL | re_mod.IGNORECASE):
            try:
                data = json.loads(m.group(1).strip())
                results.append(data)
            except: pass
        return results

    @staticmethod
    def extract_meta_tags(html_text):
        meta = {}
        for m in re_mod.finditer(r"<meta[^>]+(?:property|name)=[\"']([^\"']+)[\"'][^>]+content=[\"']([^\"']+)[\"']", html_text, re_mod.IGNORECASE):
            meta[m.group(1)] = html.unescape(m.group(2))
        return meta

    @staticmethod
    def extract_links(html_text, base_url=""):
        links = []
        for m in re_mod.finditer(r"<a[^>]+href=[\"']([^\"']+)[\"']", html_text, re_mod.IGNORECASE):
            link = m.group(1)
            if link.startswith("http") or link.startswith("/"):
                links.append(link)
        return links[:100]

    @staticmethod
    def extract_images(html_text):
        imgs = []
        for m in re_mod.finditer(r"<img[^>]+src=[\"']([^\"']+)[\"']", html_text, re_mod.IGNORECASE):
            imgs.append(m.group(1))
        return imgs[:50]

    @staticmethod
    def extract_author(html_text):
        m = re_mod.search(r"<meta[^>]+name=[\"']author[\"'][^>]+content=[\"']([^\"']+)[\"']", html_text, re_mod.IGNORECASE)
        if m: return html.unescape(m.group(1)).strip()
        return ""

    @staticmethod
    def extract_publish_date(html_text):
        m = re_mod.search(r"<meta[^>]+property=[\"']article:published_time[\"'][^>]+content=[\"']([^\"']+)[\"']", html_text, re_mod.IGNORECASE)
        if m: return m.group(1).strip()
        m = re_mod.search(r"<time[^>]+datetime=[\"']([^\"']+)[\"']", html_text, re_mod.IGNORECASE)
        if m: return m.group(1).strip()
        return ""


class PlatformExtractors:
    @staticmethod
    def youtube(data):
        return {
            "title": data.get("title", ""), "text": data.get("description", "") or data.get("text", ""),
            "tags": "youtube," + data.get("channel", ""), "url": data.get("webpage_url", "") or data.get("url", ""),
            "author": data.get("channel", "") or data.get("uploader", ""),
            "published": str(data.get("upload_date", "") or data.get("published_at", "")),
            "metadata": {"views": data.get("view_count", 0), "duration": data.get("duration", 0), "likes": data.get("like_count", 0)},
            "content_type": "video",
        }

    @staticmethod
    def twitter(data):
        return {
            "title": "Tweet by @" + data.get("author", ""),
            "text": data.get("text", "") or data.get("full_text", ""),
            "tags": "twitter,x", "url": data.get("url", ""),
            "author": data.get("author", "") or (data.get("user", {}).get("screen_name", "") if isinstance(data.get("user"), dict) else ""),
            "published": str(data.get("created_at", "")),
            "metadata": {"retweets": data.get("retweet_count", 0), "likes": data.get("favorite_count", 0), "replies": data.get("reply_count", 0)},
            "content_type": "tweet",
        }

    @staticmethod
    def github(data):
        return {
            "title": data.get("title", "") or data.get("full_name", ""),
            "text": data.get("description", "") or data.get("body", ""),
            "tags": "github," + data.get("language", ""),
            "url": data.get("html_url", "") or data.get("url", ""),
            "author": data.get("owner", {}).get("login", "") if isinstance(data.get("owner"), dict) else data.get("user", ""),
            "published": str(data.get("created_at", "")),
            "metadata": {"stars": data.get("stargazers_count", 0), "forks": data.get("forks_count", 0), "issues": data.get("open_issues_count", 0)},
            "content_type": "code",
        }

    @staticmethod
    def reddit(data):
        return {
            "title": data.get("title", ""),
            "text": data.get("selftext", "") or data.get("text", ""),
            "tags": "reddit," + data.get("subreddit", ""),
            "url": data.get("url", "") or "https://www.reddit.com" + (data.get("permalink", "") or ""),
            "author": data.get("author", ""),
            "published": str(data.get("created_utc", "") or data.get("created_at", "")),
            "metadata": {"ups": data.get("ups", 0), "downs": data.get("downs", 0), "comments": data.get("num_comments", 0)},
            "content_type": "post",
        }

    @staticmethod
    def zhihu(data):
        return {
            "title": data.get("title", ""),
            "text": data.get("content", "") or data.get("text", ""),
            "tags": "zhihu," + data.get("topic", ""),
            "url": data.get("url", ""),
            "author": data.get("author", {}).get("name", "") if isinstance(data.get("author"), dict) else data.get("author", ""),
            "published": str(data.get("created", "") or data.get("created_at", "")),
            "metadata": {"voteup": data.get("voteup_count", 0), "comments": data.get("comment_count", 0)},
            "content_type": "article",
        }

    @staticmethod
    def generic(data):
        return {
            "title": data.get("title", ""),
            "text": data.get("text", "") or data.get("content", "") or str(data)[:50000],
            "tags": "web," + data.get("platform", ""),
            "url": data.get("url", ""),
            "author": data.get("author", ""),
            "published": data.get("published", "") or data.get("date", ""),
            "metadata": data.get("metadata", {}),
            "content_type": data.get("content_type", "webpage"),
        }


PLATFORM_EXTRACTOR_MAP = {
    "youtube": PlatformExtractors.youtube,
    "twitter": PlatformExtractors.twitter,
    "github": PlatformExtractors.github,
    "reddit": PlatformExtractors.reddit,
    "zhihu": PlatformExtractors.zhihu,
    "bilibili": PlatformExtractors.generic,
}

def get_extractor(platform):
    return PLATFORM_EXTRACTOR_MAP.get(platform.lower(), PlatformExtractors.generic)
