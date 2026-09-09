from feed_utils import build_news_file

# Define standard categories with multiple feed sources mapped to them
CONFIG = {
    "World": {
        "CNN": "https://news.google.com/rss/search?q=site%3Acnn.com%20world&hl=en-US&gl=US&ceid=US%3Aen",
        "Yahoo": "https://news.google.com/rss/search?q=site%3Ayahoo.com%2Fnews%20world&hl=en-US&gl=US&ceid=US%3Aen"
    },
    "Business": {
        "CNN": "https://news.google.com/rss/search?q=site%3Acnn.com%20business&hl=en-US&gl=US&ceid=US%3Aen",
        "Yahoo": "https://news.google.com/rss/search?q=site%3Afinance.yahoo.com&hl=en-US&gl=US&ceid=US%3Aen"
    },
    "Technology": {
        "CNN": "https://news.google.com/rss/search?q=site%3Acnn.com%20technology&hl=en-US&gl=US&ceid=US%3Aen",
        "Yahoo": "https://www.yahoo.com/tech/rss"
    },
    "Entertainment": {
        "CNN": "https://news.google.com/rss/search?q=site%3Acnn.com%20entertainment&hl=en-US&gl=US&ceid=US%3Aen",
        "Yahoo": "https://news.google.com/rss/search?q=site%3Ayahoo.com%20entertainment&hl=en-US&gl=US&ceid=US%3Aen"
    }
}

def fetch_merged_news():
    output = build_news_file(CONFIG, "merged_news.json", source_field="source")
    print(f"\nSuccess! Merged news saved to: '{output}'")

if __name__ == "__main__":
    fetch_merged_news()
