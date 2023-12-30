# Firehose - A mass media monitoring tool.
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import feedparser

# === CONFIG ===
DateCutoff = 2  # Don't parse stories older than x days.

# Sources is a set to prevent dupe issues
sources = set([])
blacklist = set([])
"""
This is a dictionary in the format of 
Key - URL
Value - [Title, Publish date, Article Text]
"""
pending_stories = dict()
read_stories = []
def parse_blacklist(path):
    global blacklist
    # Read the entire content of the file
    file = open(path, "r")
    content = file.read()
    blacklist = sorted( re.findall(r'\"(.*?)\"', content), key=len, reverse=True)

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

    print(f"Loaded {len(sources)} sources.")


def parse_feed(url):
    """
    Parse individual feed and return stories.
    """
    current_time = datetime.now()
    stories = []
    feed = feedparser.parse(url)
    feed_title = feed.feed.get('title', 'No Title Available')
    print(f"\nParsing feed: {feed_title} ({url})")

    for entry in feed.entries:
        published_str = entry.get('published', '')
        published_date = parse_published_date(published_str)

        if published_date and current_time - published_date < timedelta(days=DateCutoff):
            story_url = entry.get('link', "ERR")
            if story_url != "ERR" and story_url not in pending_stories:
                stories.append((story_url, entry.get('title', 'Title Unavailable'), published_str, get_article_text(story_url)))
                print(f"found story - {stories[-1][1]}")

    return stories

def get_stories():
    """
    Load all stories from the source list using multithreading.
    """
    with ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(parse_feed, url): url for url in sources}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                stories = future.result()
                for story in stories:
                    url = story[0]
                    if url not in pending_stories:
                        pending_stories[url] = story[1:]
            except Exception as exc:
                print(f'{url} generated an exception: {exc}')


def get_article_text(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        txt = clean_text(soup.get_text().strip())
        print(txt)
        return txt
    else:
        return "Error parsing text."

def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    stripped_lines = [line.rstrip() for line in text.split('\n')]
    text = '\n'.join(stripped_lines)
    text = re.sub(r'\s+', ' ', text)
    for item in blacklist:
        text = text.replace(item, "")
    return text

def parse_published_date(published_str):
    """
    Convert the published string to a datetime object.
    """
    try:
        return datetime(*time.strptime(published_str, '%a, %d %b %Y %H:%M:%S %z')[:6])
    except ValueError:
        return None


if __name__ == "__main__":
    start = time.time()
    print("You are running Firehose as the main file, checking sources and stories")
    parse_sources("Firehose2/Data/FirehoseSources.txt")
    parse_blacklist("Firehose2/Data/Blacklist.txt")
    print(f"{len(blacklist)} blacklist items")
    get_stories()
    print(f"Found {len(pending_stories)} ready to be parsed!")
    print(f"This took {time.time() - start} seconds!")
    client = AIDAL.init()
    print("parsing with AI")
    for story in pending_stories.keys():
        content = pending_stories[story]
        AI_response = AIDAL.summarise_article(client, (content[0] + "\n" + content[1] + "\n" + content[2]))
        print(AI_response)
        read_stories.append([story, content[0], content[1], content[2], AI_response])



