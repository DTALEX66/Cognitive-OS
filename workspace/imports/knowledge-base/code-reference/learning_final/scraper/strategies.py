"""Strategy Chain - Multi-strategy fallback for any platform"""
from __future__ import annotations
from typing import Any, Optional, Callable
from enum import Enum
import json, time, urllib.request, urllib.parse, ssl, re as re_mod, random

class StrategyType(str, Enum):
    PLAYWRIGHT = "playwright"
    API_OFFICIAL = "api_official"
    API_INTERNAL = "api_internal"
    GRAPHQL = "graphql"
    HTTP = "http"
    CURL_CFFI = "curl_cffi"
    HTTPX = "httpx"
    RSS = "rss"
    ARCHIVE = "archive"
    LLM = "llm"
    NATIVE = "native"
    MARKDOWNIFY = "markdownify"
    SCRAPLING = "scrapling"


class StrategyResult:
    def __init__(self, success, data=None, error="", strategy=None, platform="", duration_ms=0.0, cached=False):
        self.success = success
        self.data = data
        self.error = error
        self.strategy = strategy or StrategyType.HTTP
        self.platform = platform
        self.duration_ms = duration_ms
        self.cached = cached

    def to_card(self, normalizer=None):
        if not self.data: return {}
        if normalizer: return normalizer(self.data)
        return {
            "title": self.data.get("title", ""),
            "content": self.data.get("text", "") or self.data.get("content", "") or json.dumps(self.data, ensure_ascii=False)[:50000],
            "tags": self.platform,
            "source_url": self.data.get("url", ""),
            "source_type": self.platform,
            "strategy": self.strategy.value,
        }


class HTTPStrategy:
    @staticmethod
    def fetch(url, headers=None, timeout=30):
        start = time.time()
        try:
            hdrs = {"User-Agent": "Mozilla/5.0"}
            if headers: hdrs.update(headers)
            req = urllib.request.Request(url, headers=hdrs)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                raw = r.read()
                ct = r.headers.get("Content-Type", "")
                text = raw.decode("utf-8", "replace")
            elapsed = (time.time() - start) * 1000
            return StrategyResult(True, {"url": url, "text": text[:500000], "content_type": ct, "headers": dict(r.headers)},
                                  strategy=StrategyType.HTTP, duration_ms=elapsed)
        except Exception as e:
            return StrategyResult(False, error=str(e), strategy=StrategyType.HTTP, duration_ms=(time.time()-start)*1000)


class CurlCFFIStrategy:
    @staticmethod
    def fetch(url, headers=None, timeout=30):
        start = time.time()
        try:
            from curl_cffi import requests as curl_req
            hdrs = {"User-Agent": "Mozilla/5.0"}
            if headers: hdrs.update(headers)
            resp = curl_req.get(url, headers=hdrs, impersonate="chrome124", timeout=timeout)
            text = resp.text[:500000]
            elapsed = (time.time() - start) * 1000
            return StrategyResult(True, {"url": url, "text": text, "status": resp.status_code, "headers": dict(resp.headers)},
                                  strategy=StrategyType.CURL_CFFI, duration_ms=elapsed)
        except Exception as e:
            return StrategyResult(False, error=str(e), strategy=StrategyType.CURL_CFFI, duration_ms=(time.time()-start)*1000)


class HttpxStrategy:
    @staticmethod
    def fetch(url, headers=None, timeout=30):
        start = time.time()
        try:
            import httpx
            hdrs = {"User-Agent": "Mozilla/5.0"}
            if headers: hdrs.update(headers)
            with httpx.Client(verify=False, http2=True, timeout=timeout) as client:
                resp = client.get(url, headers=hdrs, follow_redirects=True)
                text = resp.text[:500000]
            elapsed = (time.time() - start) * 1000
            return StrategyResult(True, {"url": url, "text": text, "status": resp.status_code, "headers": dict(resp.headers)},
                                  strategy=StrategyType.HTTPX, duration_ms=elapsed)
        except Exception as e:
            return StrategyResult(False, error=str(e), strategy=StrategyType.HTTPX, duration_ms=(time.time()-start)*1000)


class PlaywrightStrategy:
    @staticmethod
    def fetch(url, headers=None, timeout=30):
        start = time.time()
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                ctx = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    viewport={"width": 1920, "height": 1080},
                    locale="en-US",
                )
                page = ctx.new_page()
                page.goto(url, wait_until="networkidle", timeout=timeout*1000)
                md_text = page.inner_text("body")
                html_text = page.content()
                browser.close()
            elapsed = (time.time() - start) * 1000
            return StrategyResult(True, {"url": url, "text": md_text[:500000], "html": html_text[:100000], "rendered": True},
                                  strategy=StrategyType.PLAYWRIGHT, duration_ms=elapsed)
        except Exception as e:
            return StrategyResult(False, error=str(e), strategy=StrategyType.PLAYWRIGHT, duration_ms=(time.time()-start)*1000)


class MarkdownifyStrategy:
    @staticmethod
    def fetch(url, headers=None, timeout=30):
        start = time.time()
        try:
            result = CurlCFFIStrategy.fetch(url, headers=headers, timeout=timeout)
            if not result.success:
                result = HTTPStrategy.fetch(url, headers=headers, timeout=timeout)
            if not result.success:
                return result
            from markdownify import markdownify as md
            html_text = result.data.get("text", "")
            md_text = md(html_text, heading_style="ATX", strip=["script", "style"])
            elapsed = (time.time() - start) * 1000
            return StrategyResult(True, {"url": url, "text": md_text[:500000], "html": html_text[:100000], "content_type": "text/markdown"},
                                  strategy=StrategyType.MARKDOWNIFY, duration_ms=elapsed)
        except Exception as e:
            return StrategyResult(False, error=str(e), strategy=StrategyType.MARKDOWNIFY, duration_ms=(time.time()-start)*1000)


class ArchiveStrategy:
    @staticmethod
    def fetch(url, headers=None, timeout=15):
        start = time.time()
        try:
            hdrs = {"User-Agent": "Mozilla/5.0"}
            if headers: hdrs.update(headers)
            req = urllib.request.Request(f"https://web.archive.org/web/timemap/link/{url}", headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                text = r.read().decode()
            snapshots = re_mod.findall(r'<([^>]+)>; rel="memento"; datetime="([^"]+)"', text)
            if snapshots:
                latest = sorted(snapshots, key=lambda x: x[1], reverse=True)[0]
                result = HTTPStrategy.fetch(latest[0])
                if result.success:
                    result.cached = True
                    result.strategy = StrategyType.ARCHIVE
                    result.duration_ms = (time.time() - start) * 1000
                    return result
            return StrategyResult(False, error="no snapshots", duration_ms=(time.time()-start)*1000)
        except Exception as e:
            return StrategyResult(False, error=str(e), duration_ms=(time.time()-start)*1000)


class RSSStrategy:
    @staticmethod
    def fetch(url, headers=None, timeout=15):
        start = time.time()
        try:
            result = HTTPStrategy.fetch(url, headers=headers, timeout=timeout)
            if not result.success: return result
            import xml.etree.ElementTree as ET
            root = ET.fromstring(result.data["text"])
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            items = []
            for entry in root.findall(".//atom:entry", ns) or root.findall(".//item"):
                title = entry.findtext("atom:title", "", ns) or entry.findtext("title", "")
                link_el = entry.find("atom:link", ns) or entry.find("link")
                link = link_el.get("href", "") if link_el is not None and hasattr(link_el, "get") else (link_el.text if link_el is not None else "")
                summary = entry.findtext("atom:summary", "", ns) or entry.findtext("description", "")
                published = entry.findtext("atom:published", "", ns) or entry.findtext("pubDate", "")
                items.append({"title": title.strip(), "url": link.strip(), "text": summary.strip(), "published": published.strip()})
            elapsed = (time.time() - start) * 1000
            return StrategyResult(True, {"url": url, "items": items, "count": len(items)}, strategy=StrategyType.RSS, duration_ms=elapsed)
        except Exception as e:
            return StrategyResult(False, error=str(e), duration_ms=(time.time()-start)*1000)


class StrategyChain:
    def __init__(self):
        self._strategies = []

    def add(self, stype, handler):
        self._strategies.append((stype, handler))
        return self

    def execute(self, url, **kwargs):
        errors = []
        for stype, handler in self._strategies:
            try:
                result = handler(url, **kwargs)
                if result.success:
                    result.strategy = stype
                    return result
                errors.append(f"{stype.value}: {result.error[:100]}")
            except Exception as e:
                errors.append(f"{stype.value}: {e}")
        return StrategyResult(False, error="; ".join(errors))

    @staticmethod
    def default_web():
        return (StrategyChain()
                .add(StrategyType.CURL_CFFI, CurlCFFIStrategy.fetch)
                .add(StrategyType.HTTPX, HttpxStrategy.fetch)
                .add(StrategyType.HTTP, HTTPStrategy.fetch)
                .add(StrategyType.ARCHIVE, ArchiveStrategy.fetch))

    @staticmethod
    def with_playwright():
        return (StrategyChain()
                .add(StrategyType.PLAYWRIGHT, PlaywrightStrategy.fetch)
                .add(StrategyType.CURL_CFFI, CurlCFFIStrategy.fetch)
                .add(StrategyType.HTTPX, HttpxStrategy.fetch)
                .add(StrategyType.ARCHIVE, ArchiveStrategy.fetch))

    @staticmethod
    def with_rss():
        return (StrategyChain()
                .add(StrategyType.RSS, RSSStrategy.fetch)
                .add(StrategyType.CURL_CFFI, CurlCFFIStrategy.fetch)
                .add(StrategyType.MARKDOWNIFY, MarkdownifyStrategy.fetch)
                .add(StrategyType.HTTPX, HttpxStrategy.fetch)
                .add(StrategyType.ARCHIVE, ArchiveStrategy.fetch))

    @staticmethod
    def anti_bot():
        return (StrategyChain()
                .add(StrategyType.PLAYWRIGHT, PlaywrightStrategy.fetch)
                .add(StrategyType.CURL_CFFI, CurlCFFIStrategy.fetch)
                .add(StrategyType.MARKDOWNIFY, MarkdownifyStrategy.fetch)
                .add(StrategyType.HTTPX, HttpxStrategy.fetch)
                .add(StrategyType.HTTP, HTTPStrategy.fetch)
                .add(StrategyType.ARCHIVE, ArchiveStrategy.fetch))

    @staticmethod
    def all():
        return (StrategyChain()
                .add(StrategyType.RSS, RSSStrategy.fetch)
                .add(StrategyType.PLAYWRIGHT, PlaywrightStrategy.fetch)
                .add(StrategyType.CURL_CFFI, CurlCFFIStrategy.fetch)
                .add(StrategyType.MARKDOWNIFY, MarkdownifyStrategy.fetch)
                .add(StrategyType.HTTPX, HttpxStrategy.fetch)
                .add(StrategyType.HTTP, HTTPStrategy.fetch)
                .add(StrategyType.ARCHIVE, ArchiveStrategy.fetch))


# Stub: ScraplingStrategy alias for CurlCFFIStrategy
ScraplingStrategy = CurlCFFIStrategy
