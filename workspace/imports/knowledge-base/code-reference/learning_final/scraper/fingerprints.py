"""Browser fingerprint rotation for anti-bot detection bypass"""
from __future__ import annotations
from typing import Optional
import json, random, hashlib, time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.113 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
]
SCREEN_SIZES = [(1920,1080),(1366,768),(1536,864),(1440,900),(1280,720),(1680,1050),(2560,1440),(390,844),(430,932)]
LANGUAGES = ["en-US,en;q=0.9","zh-CN,zh;q=0.9,en;q=0.8","ja-JP,ja;q=0.9,en;q=0.8","ko-KR,ko;q=0.9,en;q=0.8"]

PLATFORM_HEADERS = {
    "xiaohongshu": {"origin":"https://www.xiaohongshu.com","referer":"https://www.xiaohongshu.com/explore"},
    "douyin": {"origin":"https://www.douyin.com","referer":"https://www.douyin.com/"},
    "bilibili": {"origin":"https://www.bilibili.com","referer":"https://www.bilibili.com/"},
    "zhihu": {"origin":"https://www.zhihu.com","referer":"https://www.zhihu.com/"},
    "x": {"authorization":"Bearer AAAA..."},
    "instagram": {"origin":"https://www.instagram.com","referer":"https://www.instagram.com/","x-ig-app-id":"936619743392459"},
    "weibo": {"origin":"https://weibo.com","referer":"https://weibo.com/"},
    "reddit": {"origin":"https://www.reddit.com","referer":"https://www.reddit.com/"},
}

class Fingerprint:
    def __init__(self):
        self.user_agent = random.choice(USER_AGENTS)
        self.width, self.height = random.choice(SCREEN_SIZES)
        self.lang = random.choice(LANGUAGES)
        self.timezone = random.choice(["Asia/Shanghai","America/New_York","Europe/London"])

    def to_headers(self, platform="", extra_headers=None):
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
            "Accept-Language": self.lang,
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1", "DNT": "1",
        }
        pheaders = PLATFORM_HEADERS.get(platform.lower(), {})
        if pheaders: headers.update(pheaders)
        if extra_headers: headers.update(extra_headers)
        return headers

    def to_playwright_context(self):
        is_mobile = "mobile" in self.user_agent.lower() or "iphone" in self.user_agent.lower()
        return {
            "user_agent": self.user_agent,
            "viewport": {"width": self.width, "height": self.height},
            "locale": self.lang.split(",")[0].replace("-", "_"),
            "timezone_id": self.timezone,
            "is_mobile": is_mobile, "has_touch": is_mobile,
        }

class FingerprintManager:
    def __init__(self):
        self._pool = []
        self._domain_map = {}
        self._cooldown = {}

    def acquire(self, domain=""):
        now = time.time()
        if domain and domain in self._domain_map:
            fp = self._domain_map[domain]
            if domain not in self._cooldown or now > self._cooldown[domain]:
                return fp
        fp = Fingerprint()
        if domain:
            self._domain_map[domain] = fp
            self._cooldown[domain] = now + random.uniform(60, 300)
        self._pool.append(fp)
        return fp

    def rotate(self, domain=""):
        if domain in self._domain_map: del self._domain_map[domain]
        if domain in self._cooldown: del self._cooldown[domain]
        return self.acquire(domain)

    def get_pool_size(self): return len(self._pool)
