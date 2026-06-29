"""Anti-Bot Detection Engine"""
from __future__ import annotations
import re, json, time, random

WAF_SIGNATURES = {
    "cloudflare": ["cloudflare", "__cfduid", "cf-ray", "cf-browser-verification", "__cf_chl"],
    "akamai": ["akamai", "akamaized", "ak-bmsc"],
    "incapsula": ["incapsula", "visid_incap"],
    "imperva": ["imperva", "_incap_"],
    "aws_waf": ["awswaf", "AWSALB"],
    "safedog": ["safedog"],
    "yundun": ["yundun", u"u963fu91ccu4e91u76fe"],
    "tencent_waf": ["waf.tencent", "tsec"],
    "baidu_yunjiasu": ["baiduyunjiasu", "yunjiasu"],
}

ANTI_BOT_CHALLENGES = [
    "just a moment", "checking your browser", "verify you are human",
    "captcha", "security check",
    "cf-browser-verification", "challenge-platform",
    r"enable javascript", r"please enable javascript",
    u"u68c0u6d4bu6d4fuff89u5668", u"u4ebau673au9a8cu8bc1",
]

class AntiBotDetector:
    @staticmethod
    def detect_waf(response_text, headers):
        detected = []
        text_lower = response_text.lower() if response_text else ""
        for waf_name, patterns in WAF_SIGNATURES.items():
            for p in patterns:
                if p.lower() in text_lower or p.lower() in json.dumps(headers).lower():
                    detected.append(waf_name)
                    break
        return detected

    @staticmethod
    def is_blocked(response_text, status_code):
        if status_code in (403, 429, 503):
            text_lower = response_text.lower() if response_text else ""
            for challenge in ANTI_BOT_CHALLENGES:
                if challenge.lower() in text_lower:
                    return True, f"WAF block: {challenge[:50]}"
            if status_code == 429: return True, "Rate limited (429)"
            if status_code == 403: return True, "Access forbidden (403)"
            if status_code == 503: return True, "Service unavailable (503)"
        return False, ""

    @staticmethod
    def detect_captcha(response_text):
        if not response_text: return False
        patterns = ["g-recaptcha", "recaptcha/api", "hcaptcha.com", "turnstile", "cf-turnstile"]
        for p in patterns:
            if p in response_text.lower():
                return True
        return False

    @staticmethod
    def detect_js_challenge(response_text):
        if not response_text: return False
        patterns = ["challenge-platform", "cf-chl-widget", "__cf_chl_opt", "__cf_chl_f_tk"]
        for p in patterns:
            if p in response_text.lower():
                return True
        return False

class CookieManager:
    def __init__(self):
        self._cookies = {}

    def set_cookies(self, domain, cookies):
        if domain not in self._cookies:
            self._cookies[domain] = {}
        self._cookies[domain].update(cookies)

    def get_cookies(self, domain):
        return self._cookies.get(domain, {})

    def format_cookie_header(self, domain):
        cookies = self.get_cookies(domain)
        return "; ".join(f"{k}={v}" for k, v in cookies.items())

    def has_cookies(self, domain):
        return domain in self._cookies and bool(self._cookies[domain])
