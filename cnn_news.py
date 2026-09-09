from feed_utils import build_news_file

# Define CNN RSS feeds categorized by topic
FEEDS = {
    "Top Stories": "https://news.google.com/rss/search?q=site%3Acnn.com&hl=en-US&gl=US&ceid=US%3Aen",
    "World": "https://news.google.com/rss/search?q=site%3Acnn.com%20world&hl=en-US&gl=US&ceid=US%3Aen",
    "Business": "https://news.google.com/rss/search?q=site%3Acnn.com%20business&hl=en-US&gl=US&ceid=US%3Aen",
    "Entertainment": "https://news.google.com/rss/search?q=site%3Acnn.com%20entertainment&hl=en-US&gl=US&ceid=US%3Aen",
    "Technology": "https://news.google.com/rss/search?q=site%3Acnn.com%20technology&hl=en-US&gl=US&ceid=US%3Aen"
}

def fetch_cnn_news():
    output = build_news_file(FEEDS, "cnn_news.json")
    print(f"\nSuccess! CNN news saved to: '{output}'")

if __name__ == "__main__":
    # Remember to run 'pip install feedparser' if you haven't already
    fetch_cnn_news()
