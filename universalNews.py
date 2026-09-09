from feed_utils import build_news_file

# Multi-source blueprint mapped to high-level categories
NEWS_MATRIX = {
    "Technology": {
        "TechCrunch": "https://techcrunch.com/feed/",
        "The Verge": "https://www.theverge.com/rss/index.xml"
    },
    "Global News": {
        "ABC News": "https://feeds.abcnews.com/abcnews/internationalheadlines",
        "NY Times": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
    },
    "Business": {
        "BBC": "https://feeds.bbci.co.uk/news/business/rss.xml"
    }
}

def build_universal_feed():
    output = build_news_file(
        NEWS_MATRIX, "master_news_hub.json", source_field="publisher"
    )
    print(f"\nCompleted! Unified feed generated at: '{output}'")

if __name__ == "__main__":
    build_universal_feed()
