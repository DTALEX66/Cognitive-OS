"""Platform Registry - 50+ platforms with auto-detection and strategy configs"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
from .strategies import StrategyChain, StrategyType
import re, json

@dataclass
class PlatformConfig:
    name: str
    domain_patterns: list
    strategy: Any = None
    api_endpoints: dict = None
    rate_limit_rps: float = 10.0
    requires_auth: bool = False
    js_required: bool = False
    content_type: str = "webpage"
    auth_type: str = ""
    proxy_recommended: bool = False
    notes: str = ""

    def __post_init__(self):
        if self.strategy is None:
            self.strategy = StrategyChain.default_web()
        if self.api_endpoints is None:
            self.api_endpoints = {}

PLATFORM_REGISTRY = {}

def register(name, config):
    PLATFORM_REGISTRY[name] = config

def register_many(configs):
    PLATFORM_REGISTRY.update(configs)

# ========== SOCIAL MEDIA ==========
register("youtube", PlatformConfig(name="YouTube", domain_patterns=[r"youtube\.com", r"youtu\.be"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=60, js_required=True,
    api_endpoints={"search":"https://www.googleapis.com/youtube/v3/search","video":"https://www.googleapis.com/youtube/v3/videos","innertube":"https://www.youtube.com/youtubei/v1"},
    auth_type="api_key", content_type="video"))

register("twitter", PlatformConfig(name="X / Twitter", domain_patterns=[r"twitter\.com", r"x\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=30, js_required=True,
    api_endpoints={"api_v2":"https://api.twitter.com/2","graphql":"https://api.twitter.com/graphql"},
    auth_type="oauth", content_type="tweet"))

register("instagram", PlatformConfig(name="Instagram", domain_patterns=[r"instagram\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10, js_required=True, requires_auth=True,
    api_endpoints={"graphql":"https://www.instagram.com/graphql/query"},
    auth_type="cookie", proxy_recommended=True, notes="Requires login cookies"))

register("tiktok", PlatformConfig(name="TikTok", domain_patterns=[r"tiktok\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=5, js_required=True, requires_auth=True,
    proxy_recommended=True, notes="Heavy obfuscation, signature required"))

register("xiaohongshu", PlatformConfig(name=u"u5c0fu7ea2u4e66", domain_patterns=[r"xiaohongshu\.com", r"xhslink\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=5, js_required=True, requires_auth=True,
    proxy_recommended=True, notes="X-S/X-T signature required"))

register("douyin", PlatformConfig(name=u"u6296u97f3", domain_patterns=[r"douyin\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=5, js_required=True, requires_auth=True,
    proxy_recommended=True, notes="X-Bogus signature, WASM obfuscation"))

register("bilibili", PlatformConfig(name="Bilibili", domain_patterns=[r"bilibili\.com", r"b23\.tv"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=30,
    api_endpoints={"api":"https://api.bilibili.com/x","search":"https://api.bilibili.com/x/web-interface/search/all/v2"},
    content_type="video"))

register("zhihu", PlatformConfig(name=u"u77e5u4e4e", domain_patterns=[r"zhihu\.com"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=10,
    api_endpoints={"api":"https://www.zhihu.com/api/v4"}, content_type="article"))

register("weibo", PlatformConfig(name=u"u5faeu535a", domain_patterns=[r"weibo\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10, js_required=True,
    auth_type="cookie", content_type="post"))

register("reddit", PlatformConfig(name="Reddit", domain_patterns=[r"reddit\.com"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=60,
    api_endpoints={"api":"https://www.reddit.com/api","oauth":"https://oauth.reddit.com"}, content_type="post"))

register("linkedin", PlatformConfig(name="LinkedIn", domain_patterns=[r"linkedin\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=5, js_required=True, requires_auth=True,
    proxy_recommended=True, notes="Requires login, heavily restricted"))

register("facebook", PlatformConfig(name="Facebook", domain_patterns=[r"facebook\.com", r"fb\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=5, js_required=True, requires_auth=True,
    proxy_recommended=True, notes="Requires login, strict anti-scraping"))

register("telegram", PlatformConfig(name="Telegram", domain_patterns=[r"t\.me", r"telegram\.org"],
    strategy=StrategyChain.default_web(), rate_limit_rps=30,
    api_endpoints={"api":"https://api.telegram.org/bot"}, auth_type="api_key", content_type="message"))

# ========== CHINESE TECH ==========
register("baidu", PlatformConfig(name=u"u767eu5ea6", domain_patterns=[r"baidu\.com"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=10, api_endpoints={"search":"https://www.baidu.com/s"}))

register("baijiahao", PlatformConfig(name=u"u767eu5bb6u53f7", domain_patterns=[r"baijiahao\.baidu\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10, js_required=True))

register("toutiao", PlatformConfig(name=u"u4ecau65e5u5934u6761", domain_patterns=[r"toutiao\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10, js_required=True))

register("jianshu", PlatformConfig(name=u"u7b80u4e66", domain_patterns=[r"jianshu\.com"],
    strategy=StrategyChain.default_web(), rate_limit_rps=20))

register("csdn", PlatformConfig(name="CSDN", domain_patterns=[r"csdn\.net"],
    strategy=StrategyChain.default_web(), rate_limit_rps=20))

register("juejin", PlatformConfig(name=u"u6398u91d1", domain_patterns=[r"juejin\.cn", r"juejin\.im"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=30, content_type="article"))

register("36kr", PlatformConfig(name="36Kr", domain_patterns=[r"36kr\.com"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=20))

register("huxiu", PlatformConfig(name=u"u864eu55dc", domain_patterns=[r"huxiu\.com"],
    strategy=StrategyChain.default_web(), rate_limit_rps=20))

register("geekbang", PlatformConfig(name=u"u6781u5ba2u90a6", domain_patterns=[r"geekbang\.org", r"infoq\.cn"],
    strategy=StrategyChain.default_web(), rate_limit_rps=20))

# ========== DEVELOPER PLATFORMS ==========
register("github", PlatformConfig(name="GitHub", domain_patterns=[r"github\.com"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=60,
    api_endpoints={"api":"https://api.github.com"}, auth_type="api_key", content_type="code"))

register("gitlab", PlatformConfig(name="GitLab", domain_patterns=[r"gitlab\.com"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=60,
    api_endpoints={"api":"https://gitlab.com/api/v4"}, auth_type="api_key", content_type="code"))

register("stackoverflow", PlatformConfig(name="Stack Overflow", domain_patterns=[r"stackoverflow\.com", r"stackexchange\.com"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=30,
    api_endpoints={"api":"https://api.stackexchange.com/2.3"}, content_type="qna"))

register("medium", PlatformConfig(name="Medium", domain_patterns=[r"medium\.com"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=20))

register("devto", PlatformConfig(name="Dev.to", domain_patterns=[r"dev\.to"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=30))

register("hackernews", PlatformConfig(name="Hacker News", domain_patterns=[r"news\.ycombinator\.com"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=60,
    api_endpoints={"api":"https://hacker-news.firebaseio.com/v0"}, content_type="news"))

# ========== NEWS & MEDIA ==========
register("nytimes", PlatformConfig(name="New York Times", domain_patterns=[r"nytimes\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10, notes="Paywall"))

register("theguardian", PlatformConfig(name="The Guardian", domain_patterns=[r"theguardian\.com"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=20))

register("bbc", PlatformConfig(name="BBC", domain_patterns=[r"bbc\.com", r"bbc\.co\.uk"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=30))

register("reuters", PlatformConfig(name="Reuters", domain_patterns=[r"reuters\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10))

register("bloomberg", PlatformConfig(name="Bloomberg", domain_patterns=[r"bloomberg\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10, notes="Paywall"))

register("cnn", PlatformConfig(name="CNN", domain_patterns=[r"cnn\.com"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=20))

register("wsj", PlatformConfig(name="Wall Street Journal", domain_patterns=[r"wsj\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10, notes="Strict paywall"))

register("economist", PlatformConfig(name="The Economist", domain_patterns=[r"economist\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10, notes="Paywall"))

# ========== CHINESE NEWS ==========
register("sina", PlatformConfig(name=u"u65b0u6d6a", domain_patterns=[r"sina\.com\.cn"],
    strategy=StrategyChain.default_web(), rate_limit_rps=20))

register("sohu", PlatformConfig(name=u"u641cu72d0", domain_patterns=[r"sohu\.com"],
    strategy=StrategyChain.default_web(), rate_limit_rps=20))

register("netease", PlatformConfig(name=u"u7f51u6613", domain_patterns=[r"163\.com"],
    strategy=StrategyChain.default_web(), rate_limit_rps=20))

register("thepaper", PlatformConfig(name=u"u6f8eu6e43u65b0u95fb", domain_patterns=[r"thepaper\.cn"],
    strategy=StrategyChain.default_web(), rate_limit_rps=20))

register("guancha", PlatformConfig(name=u"u89c2u5bdfu8005", domain_patterns=[r"guancha\.cn"],
    strategy=StrategyChain.default_web(), rate_limit_rps=20))

# ========== E-COMMERCE ==========
register("amazon", PlatformConfig(name="Amazon", domain_patterns=[r"amazon\.com", r"amazon\.co\.uk", r"amazon\.de", r"amazon\.jp", r"amazon\.cn"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=5, js_required=True, proxy_recommended=True,
    notes="Aggressive anti-scraping, CAPTCHA often triggered"))

register("taobao", PlatformConfig(name=u"u6dd8u5b9d", domain_patterns=[r"taobao\.com", r"tmall\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=5, js_required=True, proxy_recommended=True,
    notes="Heavy anti-scraping, login required"))

register("jd", PlatformConfig(name=u"u4eacu4e1c", domain_patterns=[r"jd\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10, js_required=True))

register("pinduoduo", PlatformConfig(name=u"u62fcu591au591a", domain_patterns=[r"pinduoduo\.com", r"yangkeduo\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=5, js_required=True, requires_auth=True,
    proxy_recommended=True, notes="Highly obfuscated"))

register("ebay", PlatformConfig(name="eBay", domain_patterns=[r"ebay\.com"],
    strategy=StrategyChain.default_web(), rate_limit_rps=20,
    api_endpoints={"api":"https://api.ebay.com/ws/api.dll"}))

register("etsy", PlatformConfig(name="Etsy", domain_patterns=[r"etsy\.com"],
    strategy=StrategyChain.default_web(), rate_limit_rps=20))

# ========== VIDEO / STREAMING ==========
register("netflix", PlatformConfig(name="Netflix", domain_patterns=[r"netflix\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=3, js_required=True, requires_auth=True,
    proxy_recommended=True, notes="Requires paid subscription"))

register("twitch", PlatformConfig(name="Twitch", domain_patterns=[r"twitch\.tv"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=20,
    api_endpoints={"api":"https://api.twitch.tv/helix"}, auth_type="api_key"))

register("vimeo", PlatformConfig(name="Vimeo", domain_patterns=[r"vimeo\.com"],
    strategy=StrategyChain.default_web(), rate_limit_rps=20,
    api_endpoints={"api":"https://api.vimeo.com"}, auth_type="api_key"))

# ========== PODCAST / AUDIO ==========
register("spotify", PlatformConfig(name="Spotify", domain_patterns=[r"spotify\.com", r"open\.spotify\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10,
    api_endpoints={"api":"https://api.spotify.com/v1"}, auth_type="api_key"))

register("soundcloud", PlatformConfig(name="SoundCloud", domain_patterns=[r"soundcloud\.com"],
    strategy=StrategyChain.default_web(), rate_limit_rps=20,
    api_endpoints={"api":"https://api.soundcloud.com"}))

# ========== FORUMS ==========
register("quora", PlatformConfig(name="Quora", domain_patterns=[r"quora\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10, js_required=True,
    requires_auth=True, notes="Requires login"))

register("4chan", PlatformConfig(name="4chan", domain_patterns=[r"4chan\.org"],
    strategy=StrategyChain.default_web(), rate_limit_rps=30,
    api_endpoints={"api":"https://a.4cdn.org"}))

register("discord", PlatformConfig(name="Discord", domain_patterns=[r"discord\.com", r"discord\.gg"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10, requires_auth=True,
    api_endpoints={"api":"https://discord.com/api/v9"}, notes="Requires auth token"))

# ========== DOCS & KNOWLEDGE ==========
register("wikipedia", PlatformConfig(name="Wikipedia", domain_patterns=[r"wikipedia\.org"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=100,
    api_endpoints={"api":"https://en.wikipedia.org/w/api.php"}, content_type="article"))

register("arxiv", PlatformConfig(name="arXiv", domain_patterns=[r"arxiv\.org"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=30,
    api_endpoints={"api":"http://export.arxiv.org/api/query"}, content_type="paper"))

register("semantic_scholar", PlatformConfig(name="Semantic Scholar", domain_patterns=[r"semanticscholar\.org"],
    strategy=StrategyChain.default_web(), rate_limit_rps=30,
    api_endpoints={"api":"https://api.semanticscholar.org/graph/v1"}, content_type="paper"))

register("papers_with_code", PlatformConfig(name="Papers with Code", domain_patterns=[r"paperswithcode\.com"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=20,
    api_endpoints={"api":"https://paperswithcode.com/api/v1"}))

# ========== AI / LLM PLATFORMS ==========
register("huggingface", PlatformConfig(name="Hugging Face", domain_patterns=[r"huggingface\.co"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=30,
    api_endpoints={"api":"https://huggingface.co/api"}, content_type="model"))

register("openai", PlatformConfig(name="OpenAI", domain_patterns=[r"openai\.com", r"platform\.openai\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10))

register("anthropic", PlatformConfig(name="Anthropic", domain_patterns=[r"anthropic\.com", r"claude\.ai", r"docs\.anthropic\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10))

register("google_ai", PlatformConfig(name="Google AI", domain_patterns=[r"ai\.google\.com", r"makersuite\.google\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10))

# ========== ENTERPRISE ==========
register("atlassian", PlatformConfig(name="Atlassian", domain_patterns=[r"atlassian\.net", r"jira\.com", r"confluence\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10, requires_auth=True, notes="Requires workspace login"))

register("salesforce", PlatformConfig(name="Salesforce", domain_patterns=[r"salesforce\.com", r"force\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=5, requires_auth=True, notes="Requires login"))

register("slack", PlatformConfig(name="Slack", domain_patterns=[r"slack\.com"],
    strategy=StrategyChain.default_web(), rate_limit_rps=30,
    api_endpoints={"api":"https://slack.com/api"}, auth_type="api_key"))

register("figma", PlatformConfig(name="Figma", domain_patterns=[r"figma\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=10, requires_auth=True,
    api_endpoints={"api":"https://api.figma.com/v1"}))

# ========== JOURNALS & DATABASES ==========
register("ieee", PlatformConfig(name="IEEE Xplore", domain_patterns=[r"ieeexplore\.ieee\.org"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=5, js_required=True,
    requires_auth=True, notes="Requires institutional access or subscription"))

register("acm", PlatformConfig(name="ACM Digital Library", domain_patterns=[r"dl\.acm\.org"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=5, js_required=True,
    requires_auth=True, notes="Requires subscription"))

register("springer", PlatformConfig(name="Springer", domain_patterns=[r"springer\.com", r"link\.springer\.com"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=10,
    api_endpoints={"api":"https://api.springernature.com/meta/v1/json"}, auth_type="api_key"))

register("nature", PlatformConfig(name="Nature", domain_patterns=[r"nature\.com"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=10))

register("sciencedirect", PlatformConfig(name="ScienceDirect", domain_patterns=[r"sciencedirect\.com"],
    strategy=StrategyChain.with_playwright(), rate_limit_rps=5, js_required=True,
    notes="Paywall, institutional access required"))

register("pubmed", PlatformConfig(name="PubMed", domain_patterns=[r"pubmed\.ncbi\.nlm\.nih\.gov", r"ncbi\.nlm\.nih\.gov"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=30,
    api_endpoints={"api":"https://eutils.ncbi.nlm.nih.gov/entrez/eutils"}, notes="Free access via E-utilities"))

register("google_scholar", PlatformConfig(name="Google Scholar", domain_patterns=[r"scholar\.google\.com"],
    strategy=StrategyChain.default_web(), rate_limit_rps=5, notes="Heavily rate limited"))

register("researchgate", PlatformConfig(name="ResearchGate", domain_patterns=[r"researchgate\.net"],
    strategy=StrategyChain.default_web(), rate_limit_rps=10,
    notes="Requires login for full content"))

# ========== CODE HOSTING & PACKAGES ==========
register("npm", PlatformConfig(name="npm", domain_patterns=[r"npmjs\.com", r"npm\.js"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=30,
    api_endpoints={"api":"https://registry.npmjs.org"}, content_type="package"))

register("pypi", PlatformConfig(name="PyPI", domain_patterns=[r"pypi\.org"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=30,
    api_endpoints={"api":"https://pypi.org/pypi"}, content_type="package"))

register("rubygems", PlatformConfig(name="RubyGems", domain_patterns=[r"rubygems\.org"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=30,
    api_endpoints={"api":"https://rubygems.org/api/v1"}, content_type="package"))

register("crates", PlatformConfig(name="crates.io", domain_patterns=[r"crates\.io"],
    strategy=StrategyChain.with_rss(), rate_limit_rps=30,
    api_endpoints={"api":"https://crates.io/api/v1"}, content_type="package"))

# ========== GENERAL / FALLBACK ==========
register("generic", PlatformConfig(name="Generic Website", domain_patterns=[".*"],
    strategy=StrategyChain.default_web(), rate_limit_rps=10))


# ========== URL ROUTER ==========
def detect_platform(url):
    url_lower = url.lower()
    results = []
    for name, config in PLATFORM_REGISTRY.items():
        if name == "generic": continue
        for pattern in config.domain_patterns:
            if re.search(pattern, url_lower):
                results.append((len(pattern), name, config))
    if results:
        results.sort(key=lambda x: -x[0])
        return results[0][1], results[0][2]
    return "generic", PLATFORM_REGISTRY["generic"]

def list_platforms(category=""):
    platforms = []
    for name, config in PLATFORM_REGISTRY.items():
        if name == "generic": continue
        platforms.append({
            "name": config.name, "key": name,
            "requires_auth": config.requires_auth,
            "js_required": config.js_required,
            "rate_limit": config.rate_limit_rps,
            "content_type": config.content_type,
            "auth_type": config.auth_type,
            "proxy_recommended": config.proxy_recommended,
            "notes": config.notes,
        })
    return sorted(platforms, key=lambda x: x["name"])
