from feed_utils import build_news_file

# Define Yahoo News RSS feeds categorized by topic
FEEDS = {
    "Top Stories": "https://news.google.com/rss/search?q=site%3Ayahoo.com%2Fnews&hl=en-US&gl=US&ceid=US%3Aen",
    "World": "https://news.google.com/rss/search?q=site%3Ayahoo.com%2Fnews%20world&hl=en-US&gl=US&ceid=US%3Aen",
    "Business": "https://news.google.com/rss/search?q=site%3Afinance.yahoo.com&hl=en-US&gl=US&ceid=US%3Aen",
    "Technology": "https://www.yahoo.com/tech/rss",
    "Entertainment": "https://news.google.com/rss/search?q=site%3Ayahoo.com%20entertainment&hl=en-US&gl=US&ceid=US%3Aen",
    "Science": "https://news.google.com/rss/search?q=site%3Ayahoo.com%2Fnews%20science&hl=en-US&gl=US&ceid=US%3Aen"
}

def fetch_yahoo_news():
    output = build_news_file(FEEDS, "yahoo_news.json")
    print(f"\nSuccess! Yahoo news saved to: '{output}'")

if __name__ == "__main__":
    # Remember to run 'pip install feedparser' if you haven't already
    fetch_yahoo_news()
