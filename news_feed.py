from datetime import datetime, timezone

from feed_utils import BASE_DIR, collect_news
from cis_storage import write_json_atomic

# Define the RSS feeds categorized by topic
FEEDS = {
    "Technology": {"BBC News": "https://feeds.bbci.co.uk/news/technology/rss.xml"},
    "Business": {"BBC News": "https://feeds.bbci.co.uk/news/business/rss.xml"},
    "Science": {"BBC News": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"},
    "World": {"BBC News": "https://feeds.bbci.co.uk/news/world/rss.xml"}
}

def fetch_categorized_news():
    data, failures = collect_news(FEEDS, source_field="source")
    data["_meta"] = {
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": sorted({source for sources in FEEDS.values() for source in sources}),
        "warnings": failures,
    }
    write_json_atomic(BASE_DIR, "news.json", data)
    output = BASE_DIR / "compuserve.db"
    for failure in failures:
        print(f"Warning: {failure}")
    print(f"\nSuccess! News successfully saved to: '{output}'")
    return output

if __name__ == "__main__":
    fetch_categorized_news()
