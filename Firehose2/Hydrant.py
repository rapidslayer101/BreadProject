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

import re
import time
from datetime import datetime, timedelta, timezone

import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dtParse


class Hydrant():

    too_old = 0
    errored_text = 0
    errored_parsing = 0
    already_done = 0

    # Sources is a set to prevent dupe issues
    sources = set([])
    blacklist = set([])
    seen_URLs = set([])

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


    def get_stories(self, sources, filter=True):
        entries_list = []
        for source in sources:
            feed = feedparser.parse(source)
            for entry in feed.entries:  # Loop through each entry in the feed
                try:
                    # Hotfix for apple newsroom since doesnt have a published, just an updated field.
                    if source == "https://www.apple.com/newsroom/rss-feed.rss":
                        entry.published = entry["updated"]
                    entry_data = {
                        'Title': entry.title,
                        'URL': entry.link,
                        'Published': dtParse.parse(entry.published),
                        'Summary': getattr(entry, 'Summary', '')}

                    if filter:
                        age = datetime.now(timezone.utc) - entry_data['Published']  # Calc article age

                        # Check we haven't tried to read this URL before
                        if self.seen_URLs.__contains__(entry_data["URL"]):
                            self.already_done += 1
                            print(f"Skipping {entry_data['Title']} since it's already been viewed.")
                        else:
                            if age <= timedelta(days=2):  # Ignore article if it's older than 2 days.
                                entry_data['Content'] = self.get_article_text(entry_data["URL"])  # Get Article

                                # Display information
                                print(f"Found Story from {feed.feed.title} ({round(age.total_seconds() / 60 / 60, 2)} hrs ago) - {entry_data['Title']}")
                                print(f"\t\t\t\t Article Text - {entry_data['Content']}")
                                entries_list.append(entry_data)
                                self.seen_URLs.add(entry_data["URL"])
                            else:
                                self.too_old += 1
                                self.seen_URLs.add(entry_data["URL"])
                    else:
                        entries_list.append(entry_data)
                except Exception as ex:
                    self.errored_parsing += 1
                    print(f"[ERROR] failed parsing source of {source} for URL {entry} with exception of {ex}")


        return entries_list

    def get_article_text(self, url):
        response = requests.get(url,  headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'})
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            txt = self.clean_text(soup.get_text().strip())
            return txt
        else:
            print(f"[ERROR] Failed parsing Article URL {url}, expected 200 response, got {response.status_code}")
            self.errored_text += 1
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


if __name__== "__main__":
    input("""You are running Hydrant as the main file NOT firehose\nPress ENTER to test the feeds.""")
    start = time.time()
    H = Hydrant()
    URLSet = H.get_stories(H.sources)
    print(f"""Stats
            Took {round((time.time() - start),2)}s
            Ready: {len(URLSet)}
            Too Old: {H.too_old}
            Errors parsing: {H.errored_parsing}
            Errors text: {H.errored_text}
            URL Blacklist size: {len(H.seen_URLs)}
            Blacklisted URL hits: {H.already_done} """)
