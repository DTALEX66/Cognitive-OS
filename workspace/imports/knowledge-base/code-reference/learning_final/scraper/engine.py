"""Universal Scraper Engine - Any Platform, Any Website, Any Company

Architecture:
  URL -> Router -> Platform Detection -> Strategy Chain -> Anti-Bot -> Extraction -> Normalization -> DB Storage

Strategy priority per platform:
  1. Native (yt-dlp, gallery-dl)
  2. Official API (if key available)
  3. Internal API (reverse-engineered)
  4. GraphQL (if known endpoint)
  5. Playwright (if JS required)
  6. curl_cffi (TLS fingerprint impersonation)
  7. RSS/Atom (if available)
  8. HTTPX (HTTP/2)
  9. HTTP (plain HTML fetch)
  10. Archive.org (fallback)

Anti-bot layers:
  - Browser fingerprint rotation (user-agent, viewport, headers)
  - TLS fingerprint impersonation (curl_cffi)
  - Full browser automation (Playwright)
  - WAF detection and classification
  - Cookie management
  - Proxy rotation
"""
from __future__ import annotations
from typing import Any, Optional, Callable
from datetime import datetime, timezone
import json, time, urllib.parse, hashlib, os, re

from .registry import PLATFORM_REGISTRY, PlatformConfig, detect_platform, list_platforms
from .strategies import StrategyChain, StrategyResult, StrategyType, HTTPStrategy, ArchiveStrategy, RSSStrategy
from .strategies import CurlCFFIStrategy, HttpxStrategy, PlaywrightStrategy, MarkdownifyStrategy
# ScraplingStrategy not available
from .cache import CacheLayer
from .router import PlatformRouter
from .fingerprints import FingerprintManager, Fingerprint
from .proxies import ProxyManager
from .antibots import AntiBotDetector, CookieManager
from .extractors import TextExtractor, get_extractor, PlatformExtractors


class UniversalScraper:
    def __init__(self, store=None):
        self._store = store
        self._cache = CacheLayer(store)
        self._router = PlatformRouter(self._cache)
        self._fingerprints = FingerprintManager()
        self._proxies = ProxyManager()
        self._cookies = CookieManager()
        self._stats = {"scraped": 0, "cached": 0, "failed": 0, "waf_blocked": 0}

    # ===== PUBLIC API =====

    def scrape(self, url, prompt="", platform_hint="", use_cache=True,
               extract_links=False, strategy_override=None):
        """Universal scrape - auto-detect platform and strategy"""
        start = time.time()
        if use_cache:
            cached = self._cache.get(url)
            if cached:
                self._stats["cached"] += 1
                return {"source": "cache", "data": cached,
                        "platform": cached.get("platform", ""),
                        "duration_ms": (time.time() - start) * 1000}

        platform_name, platform_config = self._determine_platform(url, platform_hint)
        if not platform_config:
            return {"source": "error", "error": f"Unknown platform: {platform_hint}",
                    "duration_ms": (time.time() - start) * 1000}

        domain = urllib.parse.urlparse(url).netloc
        fp = self._fingerprints.acquire(domain)
        proxy = self._proxies.get_proxy(domain)
        headers = fp.to_headers(platform_name)

        # Try native CLI tools first
        result = self._try_native(url, platform_name)
        if not result or not result.success:
            # Use strategy chain
            chain = strategy_override or platform_config.strategy
            result = chain.execute(url, headers=headers)

        if result and result.success:
            card = self._process_result(result, platform_name, url)
            if prompt and card.get("text"):
                card["summary"] = self._extract_relevant(card["text"], prompt)
            self._cache.set(url, card, ttl=900)
            saved_id = self._save_to_db(card, url)
            card["saved_id"] = saved_id
            self._stats["scraped"] += 1
            if extract_links and isinstance(result.data, dict):
                links = TextExtractor.extract_links(result.data.get("text", ""), url)
                card["found_links"] = links
            waf_detected = AntiBotDetector.detect_waf(result.data.get("text", ""), {})
            return {"source": "live", "platform": platform_name,
                    "strategy": result.strategy.value,
                    "data": card, "duration_ms": (time.time() - start) * 1000,
                    "cached": result.cached, "waf_detected": waf_detected}
        else:
            self._stats["failed"] += 1
            error_text = result.error if result else "all strategies failed"
            waf_detected = AntiBotDetector.detect_waf(error_text, {})
            if waf_detected:
                self._stats["waf_blocked"] += 1
            return {"source": "error", "platform": platform_name,
                    "error": error_text, "waf_detected": waf_detected,
                    "duration_ms": (time.time() - start) * 1000}

    def scrape_with_playwright(self, url, **kwargs):
        """Force Playwright strategy for JS-heavy sites"""
        return self.scrape(url, strategy_override=StrategyChain.with_playwright(), **kwargs)

    def scrape_with_anti_bot(self, url, **kwargs):
        """Use all anti-bot strategies"""
        return self.scrape(url, strategy_override=StrategyChain.anti_bot(), **kwargs)

    def search(self, query, platform="web", limit=10):
        """Search across platforms"""
        results = []
        fp = self._fingerprints.acquire()
        config = PLATFORM_REGISTRY.get(platform, PLATFORM_REGISTRY["generic"])

        if platform in ("web", "generic"):
            for engine_url in [
                f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}",
            ]:
                try:
                    result = CurlCFFIStrategy.fetch(engine_url, headers=fp.to_headers())
                    if result.success:
                        extracted = self._router.extract(result.data.get("text", ""))
                        if extracted.get("text"):
                            results.append({"query": query, **extracted, "platform": "web"})
                            break
                except: continue
        return results[:limit]

    def batch_scrape(self, urls, **kwargs):
        """Scrape multiple URLs sequentially"""
        return [self.scrape(u, **kwargs) for u in urls]

    def crawl(self, start_url, max_pages=10, same_domain=True, depth=2, **kwargs):
        """Crawl - follow links from starting URL"""
        from collections import deque
        visited = set()
        queue = deque([(start_url, 0)])
        results = []
        domain = urllib.parse.urlparse(start_url).netloc
        while queue and len(results) < max_pages:
            url, d = queue.popleft()
            if url in visited:
                continue
            if same_domain and urllib.parse.urlparse(url).netloc != domain:
                continue
            visited.add(url)
            if d > depth:
                continue
            result = self.scrape(url, extract_links=True, **kwargs)
            if result.get("data") and result.get("source") != "error":
                results.append(result)
                for link in result["data"].get("found_links", []):
                    if link not in visited:
                        full_url = link if link.startswith("http") else urllib.parse.urljoin(url, link)
                        queue.append((full_url, d + 1))
        return results

    def register_platform(self, name, config):
        PLATFORM_REGISTRY[name] = config

    def register_extractor(self, platform, extractor):
        from .extractors import PLATFORM_EXTRACTOR_MAP
        PLATFORM_EXTRACTOR_MAP[platform] = extractor

    def list_platforms(self, **filters):
        return list_platforms(**filters)

    def detect_waf(self, url):
        """Detect WAF protection on a URL without fully scraping"""
        try:
            import httpx
            with httpx.Client(verify=False, timeout=15) as client:
                resp = client.get(url, follow_redirects=True)
                waf = AntiBotDetector.detect_waf(resp.text, dict(resp.headers))
                blocked, reason = AntiBotDetector.is_blocked(resp.text, resp.status_code)
                return {
                    "url": url, "status": resp.status_code,
                    "waf": waf, "blocked": blocked, "reason": reason,
                    "captcha": AntiBotDetector.detect_captcha(resp.text),
                    "js_challenge": AntiBotDetector.detect_js_challenge(resp.text),
                    "headers": dict(resp.headers),
                }
        except Exception as e:
            return {"url": url, "error": str(e)}

    def stats(self):
        return {**self._stats, "cache": self._cache.stats(), "proxies": self._proxies.stats(),
                "fingerprints_pool": self._fingerprints.get_pool_size()}

    # ===== INTERNAL =====

    def _determine_platform(self, url, hint=""):
        if hint:
            cfg = PLATFORM_REGISTRY.get(hint)
            if cfg:
                return hint, cfg
        return detect_platform(url)

    def _try_native(self, url, platform):
        """Try platform-native CLI tools"""
        start = time.time()
        try:
            if platform == "youtube":
                import subprocess
                r = subprocess.run(
                    ["yt-dlp", "--flat-playlist", "--dump-json", "--no-download", url],
                    capture_output=True, text=True, timeout=30)
                if r.returncode == 0 and r.stdout.strip():
                    data = json.loads(r.stdout.strip().split(chr(10))[0])
                    return StrategyResult(True, data, platform=platform,
                                          strategy=StrategyType.NATIVE,
                                          duration_ms=(time.time()-start)*1000)
        except: pass
        try:
            if platform in ("instagram", "tiktok"):
                import subprocess
                r = subprocess.run(["gallery-dl", "--dump-json", url],
                                   capture_output=True, text=True, timeout=30)
                if r.returncode == 0 and r.stdout.strip():
                    data = json.loads(r.stdout.strip())
                    return StrategyResult(True, data, platform=platform,
                                          strategy=StrategyType.NATIVE,
                                          duration_ms=(time.time()-start)*1000)
        except: pass
        return None

    def _process_result(self, result, platform, url):
        """Extract content and normalize to card format"""
        data = result.data or {}
        text = data.get("text", "") or data.get("content", "") or str(data)

        is_html = isinstance(text, str) and ("<html" in text[:200].lower() or "<!doctype" in text[:200].lower())
        if is_html:
            extracted = self._router.extract(text, platform)
        else:
            extracted = {
                "title": data.get("title", "") or data.get("name", ""),
                "text": str(text)[:100000],
                "description": data.get("description", "") or data.get("summary", ""),
            }

        extractor = get_extractor(platform)
        try:
            card = extractor({**data, **extracted})
        except:
            card = PlatformExtractors.generic({**data, **extracted})

        card.update({
            "tags": card.get("tags", platform),
            "source_url": url,
            "source_type": result.platform or platform,
            "platform": result.platform or platform,
            "strategy": result.strategy.value,
            "cached": result.cached,
        })
        return card

    def _extract_relevant(self, text, prompt):
        """Extract relevant sections based on prompt keywords"""
        keywords = prompt.lower().split()
        if not keywords:
            return text[:2000]
        lines = text.split(chr(10))
        relevant = []
        for line in lines:
            line_lower = line.lower()
            score = sum(1 for k in keywords if k in line_lower)
            if score > 0:
                relevant.append((score, line))
        relevant.sort(key=lambda x: -x[0])
        return chr(10).join(line for _, line in relevant[:20]) or text[:2000]

    def _save_to_db(self, card, url):
        if not self._store:
            return None
        try:
            ts = datetime.now(timezone.utc).isoformat()
            cur = self._store.conn.execute(
                "INSERT INTO cards (title,content,tags,memory_strength,next_review_at,created_at,updated_at) VALUES (?,?,?,0.5,?,?,?)",
                (str(card.get("title", ""))[:500],
                 str(card.get("text", "") or card.get("content", "") or json.dumps(card, ensure_ascii=False))[:50000],
                 str(card.get("tags", ""))[:500], ts, ts, ts)
            )
            self._store.conn.commit()
            return cur.lastrowid
        except:
            return None
