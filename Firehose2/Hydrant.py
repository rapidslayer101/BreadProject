"""
       !            HYDRANT.PY
     .:::.          Proudly created by JakeR 30/12/23
    ///|\\\         A tool for grabbing RSS feeds and their content.
   {=-=-=-=}
 .-||||/..\
c[I ||||\''/
  '-||||||| 
    |||||||
    |||||||
    |||||||
   [=======]
   `"""""""`
"""

from bs4 import BeautifulSoup
import time
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import feedparser


class Hydrant():
    # Sources is a set to prevent dupe issues
    sources = set([])
    blacklist = set([])
    seen_URLs = set([])
    """
    This is a dictionary in the format of 
    Key - URL
    Value - [Title, Publish date, Article Text]
    """
    pending_stories = dict()
    read_stories = []

    def __init__(self):
        self.parse_sources("Data/FirehoseSources.txt")
        self.parse_blacklist("Data/Blacklist.txt")

    def parse_blacklist(self, path):
        # Read the entire content of the file
        file = open(path, "r")
        content = file.read()
        self.blacklist = sorted(re.findall(r'\"(.*?)\"', content), key=len, reverse=True)

    def parse_sources(self, path):
        """
        Loads sources from a given file path, lines starting with a # will be ignored.
        path: Path to firehose sources
        """
        # Read the file
        with open(path, 'r') as file:
            for line in file:
                if line[0] != "#":
                    self.sources.add(line.strip())
        print(f"Loaded {len(self.sources)} sources.")

    def get_stories(self):
        """
        Load all stories from the source list using multithreading.
        """
        self.pending_stories = []
        with ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(self.parse_feed, url): url for url in self.sources}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    stories = future.result()
                    for story in stories:
                        url = story[0]
                        if url not in self.pending_stories and url not in self.seen_URLs:
                            self.pending_stories[url] = story[1:]
                    self.seen_URLs.add(url)
                except Exception as exc:
                    print(f'{url} generated an exception: {exc}')
        return self.pending_stories

    def parse_feed(self, url):
        """
        Parse individual feed and return stories.
        """
        current_time = datetime.now()
        stories = []
        feed = feedparser.parse(url)

        for entry in feed.entries:
            published_str = entry.get('published', '')
            published_date = self.parse_published_date(published_str)

            if published_date and current_time - published_date < timedelta(days=2):
                story_url = entry.get('link', "ERR")
                if story_url != "ERR" and story_url not in self.pending_stories:
                    stories.append((story_url, entry.get('title', 'Title Unavailable'), published_str,
                                    self.get_article_text(story_url)))
                    # Updated to only print a simplified message for recent stories
                    print(f"found story - {entry.get('title', 'Title Unavailable')}")


    def get_article_text(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            txt = self.clean_text(soup.get_text().strip())
            print(txt)
            return txt
        else:
            return "Error parsing text."

    def clean_text(self, text):
        """
        Takes a string, performs several cleaning operations on it and removes any occurrences of the blacklist
        """
        text = re.sub(r'\n+', '\n', text)
        stripped_lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(stripped_lines)
        text = re.sub(r'\s+', ' ', text)
        for item in self.blacklist:
            text = text.replace(item, "")
        return text

    def parse_published_date(self, published_str):
        """
        Convert the published string to a datetime object.
        """
        try:
            return datetime(*time.strptime(published_str, '%a, %d %b %Y %H:%M:%S %z')[:6])
        except ValueError:
            return None
