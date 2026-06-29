-- 014_scraper_cache.sql
CREATE TABLE IF NOT EXISTS scraped_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_hash TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_scraped_cache_hash ON scraped_cache(url_hash);
