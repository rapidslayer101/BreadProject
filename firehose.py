# Firehose - A mass media monitoring tool.
import feedparser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
import requests

# === CONFIG ===
DateCutoff = 2  # Don't parse stories older than x days.

# Sources is a set to prevent dupe issues
sources = set([])

"""
This is a dictionary in the format of 
Key - URL
Value - [Title, Publish date, Article Text]
"""
pending_stories = dict()


def parse_sources(path):
    """
    Loads sources from a given file path, lines starting with a # will be ignored.
    path: Path to firehose sources
    """
    # Read the file
    with open(path, 'r') as file:
        for line in file:
            if line[0] != "#":
                sources.add(line.strip())

    print(f"RSS Feed parsing complete, loaded {len(sources)} sources.")


def get_stories():
    """
    Loads all stories from the source list.
    """
    current_time = datetime.now()
    for url in sources:
        feed = feedparser.parse(url)
        feed_title = feed.feed.get('title', 'No Title Available')
        print(f"\nParsing feed: {feed_title} ({url})")

        for entry in feed.entries:
            published_str = entry.get('published', '')
            published_date = parse_published_date(published_str)

            # Do not parse stories that are beyond the cut off point
            if published_date:
                if current_time - published_date >= timedelta(days=DateCutoff):
                    continue

            # Check if the story's URL is new and add it to pending_stories if it is.
            url = entry.get('link', "ERR")
            if url != "ERR" and url not in pending_stories:
                pending_stories[url] = (entry.get('title', 'Title Unavailable'), published_str, get_article_text(url))
                print(f"found story - {pending_stories[url][0]}")


def get_article_text(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        #print(soup.get_text().strip())
        return soup.get_text()
    else:
        return "Error parsing text."

def parse_published_date(published_str):
    """
    Convert the published string to a datetime object.
    """
    try:
        return datetime(*time.strptime(published_str, '%a, %d %b %Y %H:%M:%S %z')[:6])
    except ValueError:
        return None


if __name__ == "__main__":
    print("You are running Firehose as the main file, checking sources and stories")
    parse_sources("firehosesources.txt")
    get_stories()
    print(pending_stories)
    print(f"Found {len(pending_stories)} ready to be parsed!")