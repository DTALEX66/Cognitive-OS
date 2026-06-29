"""Multi-layer cache: Memory -> SQLite -> File"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional
import json, hashlib, time, sqlite3, os, threading

class CacheLayer:
    def __init__(self, store=None, db_path: str = ""):
        self._mem = {}
        self._mem_ttl = 300
        self._store = store
        self._lock = threading.Lock()
        self._stats = {"hits": 0, "misses": 0, "mem_hits": 0, "sqlite_hits": 0}
        self._db = None
        if db_path and not store:
            try:
                self._db = sqlite3.connect(db_path, check_same_thread=False)
                self._db.execute("CREATE TABLE IF NOT EXISTS scraper_cache (key TEXT PRIMARY KEY, data TEXT, expires_at REAL, created_at TEXT)")
            except: pass

    def _key(self, url_or_query, **extra):
        raw = url_or_query + json.dumps(extra, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, url, **extra):
        k = self._key(url, **extra)
        now = time.time()
        with self._lock:
            if k in self._mem:
                data, expires = self._mem[k]
                if now < expires:
                    self._stats["hits"] += 1; self._stats["mem_hits"] += 1
                    return data
                del self._mem[k]
            if self._db:
                try:
                    row = self._db.execute("SELECT data, expires_at FROM scraper_cache WHERE key=?", (k,)).fetchone()
                    if row and now < row[1]:
                        data = json.loads(row[0])
                        self._mem[k] = (data, now + self._mem_ttl)
                        self._stats["hits"] += 1; self._stats["sqlite_hits"] += 1
                        return data
                except: pass
            if self._store:
                try:
                    h = hashlib.md5(url.encode()).hexdigest()
                    row = self._store.conn.execute("SELECT data FROM scraped_cache WHERE url_hash=?", (h,)).fetchone()
                    if row:
                        data = json.loads(row[0])
                        self._stats["hits"] += 1; self._stats["sqlite_hits"] += 1
                        return data
                except: pass
        self._stats["misses"] += 1
        return None

    def set(self, url, data, ttl=900, **extra):
        k = self._key(url, **extra)
        expires = time.time() + ttl
        with self._lock:
            self._mem[k] = (data, expires)
            if self._db:
                try:
                    self._db.execute("INSERT OR REPLACE INTO scraper_cache (key,data,expires_at,created_at) VALUES (?,?,?,?)",
                                     (k, json.dumps(data, default=str), expires, datetime.now(timezone.utc).isoformat()))
                    self._db.commit()
                except: pass
            if self._store:
                try:
                    h = hashlib.md5(url.encode()).hexdigest()
                    self._store.conn.execute(
                        "INSERT OR REPLACE INTO scraped_cache (url_hash,url,data,created_at) VALUES (?,?,?,?)",
                        (h, url, json.dumps(data, default=str), datetime.now(timezone.utc).isoformat()))
                    self._store.conn.commit()
                except: pass

    def stats(self):
        with self._lock:
            return {**self._stats, "mem_size": len(self._mem)}
