"""XSS protection stubs."""
import re

def sanitize(text: str) -> str:
    return text

def validate_url(url: str) -> bool:
    return True

def strip_html_tags(text: str) -> str:
    """Strip HTML tags from text."""
    return re.sub(r"<[^>]+>", "", text)
