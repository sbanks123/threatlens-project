import json
import os
from pathlib import Path
from xml.etree import ElementTree as ET

import requests

BASE = Path(__file__).resolve().parents[1]
SAMPLE_FILE = BASE / "data" / "sample_posts.json"

LIVE_FEEDS = [
    ("thehackernews", "https://feeds.feedburner.com/TheHackersNews"),
    ("hnrss_security", "https://hnrss.org/newest?q=security"),
    ("hnrss_cyber_attack", "https://hnrss.org/newest?q=cyber+attack"),
]


def _load_sample_posts():
    if not SAMPLE_FILE.exists():
        return []
    return json.loads(SAMPLE_FILE.read_text())


def _fetch_rss(url: str, source_name: str, max_items: int = 20):
    posts = []
    try:
        r = requests.get(url, timeout=12, headers={"User-Agent": "ThreatLens/1.0"})
        if r.status_code != 200:
            return posts

        root = ET.fromstring(r.text)
        channel = root.find("channel")
        if channel is None:
            return posts

        items = channel.findall("item")[:max_items]
        for item in items:
            title = (item.findtext("title") or "").strip()
            desc = (item.findtext("description") or "").strip()
            link = (item.findtext("link") or "").strip()
            content = f"{desc} {link}".strip()
            if title or content:
                posts.append({
                    "source": source_name,
                    "title": title,
                    "content": content,
                })
    except Exception:
        pass
    return posts


def fetch_posts():
    """
    Source loader for prototype.
    - always includes sample posts
    - optional live RSS feeds when THREATLENS_ENABLE_LIVE=true
    """
    posts = _load_sample_posts()

    enable_live = os.getenv("THREATLENS_ENABLE_LIVE", "true").lower() in {"1", "true", "yes"}
    max_items = int(os.getenv("THREATLENS_LIVE_MAX_ITEMS", "10"))

    if enable_live:
        for source_name, url in LIVE_FEEDS:
            posts.extend(_fetch_rss(url, source_name, max_items=max_items))

    return posts
