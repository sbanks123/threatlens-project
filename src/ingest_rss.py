import feedparser

def fetch_hackernews():
    url = "https://feeds.feedburner.com/TheHackersNews"
    feed = feedparser.parse(url)

    posts = []
    for entry in feed.entries[:10]:
        posts.append({
            "source": "LIVE",
            "title": "[LIVE RSS] " + entry.title,
            "content": getattr(entry, "summary", ""),
        })

    return posts