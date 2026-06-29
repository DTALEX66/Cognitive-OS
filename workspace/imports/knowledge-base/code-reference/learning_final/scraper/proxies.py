"""Proxy rotation and management system"""
from __future__ import annotations
from typing import Optional
import random, time, threading, os

class ProxyManager:
    def __init__(self):
        self._proxies = []
        self._blacklist = {}
        self._fail_counts = {}
        self._lock = threading.Lock()
        self._max_fails = 3
        self._ban_seconds = 300
        self._index = 0
        self._load_from_env()

    def _load_from_env(self):
        raw = os.environ.get("SCRAPER_PROXIES", "")
        if raw:
            for p in raw.split(","):
                p = p.strip()
                if p: self._proxies.append({"url": p, "type": "http", "region": "auto", "provider": "env"})

    def add_proxy(self, url, proxy_type="http", region="auto", provider="manual"):
        with self._lock:
            self._proxies.append({"url": url, "type": proxy_type, "region": region, "provider": provider})

    def get_proxy(self, domain="", region=""):
        with self._lock:
            now = time.time()
            available = [p for p in self._proxies if p["url"] not in self._blacklist or now > self._blacklist[p["url"]]]
            if region: available = [p for p in available if p.get("region","auto") == region or p.get("region","auto") == "auto"]
            if not available: return None
            self._index = (self._index + 1) % len(available)
            return available[self._index]

    def report_failure(self, proxy_url):
        with self._lock:
            self._fail_counts[proxy_url] = self._fail_counts.get(proxy_url, 0) + 1
            if self._fail_counts[proxy_url] >= self._max_fails:
                self._blacklist[proxy_url] = time.time() + self._ban_seconds
                del self._fail_counts[proxy_url]

    def report_success(self, proxy_url):
        with self._lock:
            if proxy_url in self._fail_counts: del self._fail_counts[proxy_url]

    def stats(self):
        with self._lock:
            return {"total": len(self._proxies), "available": len([p for p in self._proxies if p["url"] not in self._blacklist])}
