import feedparser
from datetime import datetime, timedelta
import time

def read_rss_sources(file_path):
    """
    Read the RSS feed URLs from the specified file.
    """
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def parse_published_date(published_str):
    """
    Convert the published string to a datetime object.
    """
    try:
        return datetime(*time.strptime(published_str, '%a, %d %b %Y %H:%M:%S %z')[:6])
    except ValueError:
        return None

def print_news_stories(rss_urls):
    """
    Print news stories from the given list of RSS feed URLs.
    """
    current_time = datetime.now()

    story_count = 0
    for url in rss_urls:
        feed = feedparser.parse(url)
        feed_title = feed.feed.get('title', 'No Title Available')
        old_feeds = []
        print(f"\nFeed Title: {feed_title} ({url})\n")

        for entry in feed.entries:
            outdated_stories_count = 0
            published_str = entry.get('published', '')
            published_date = parse_published_date(published_str)
            bad_feed = False
            if published_date and (current_time - published_date >= timedelta(days=1)):
                outdated_stories_count += 1
                bad_feed = True
            else:
                story_count += 1
                print(f"Title: {entry.get('title', 'No Title Available')}")
                print(f"Link: {entry.get('link', 'No Link Available')}")
                print(f"Published: {published_str}\n")

        if bad_feed:
            old_feeds.append({feed,feed_title, outdated_stories_count})

        print(f"Number of Stories: {story_count}\n")
        print(f"Number of Outdated Stories: {outdated_stories_count}\n")
    print(old_feeds)

if __name__ == "__main__":
    rss_urls = read_rss_sources("firehosesources.txt")
    print_news_stories(rss_urls)
