"""Current-news refresh integration."""


def refresh(app):
    app.ansi_scroll("Updating current news wire...", 0.01)
    try:
        from news_feed import fetch_categorized_news
        output = fetch_categorized_news()
    except Exception as exc:
        app.ansi_scroll(f"Update failed; previous news edition preserved: {exc}", 0.01)
        return False
    app.ansi_scroll(f"News wire updated: {output.name}", 0.01)
    return True
