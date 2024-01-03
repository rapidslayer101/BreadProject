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
import mysql.connector
import feedparser
import mysql
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dtParse
from openai import OpenAI
import string

client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")


class Hydrant():

    too_old = 0
    errored_text = 0
    errored_parsing = 0
    already_done = 0
    LLMFilter = 0

    # Sources is a set to prevent dupe issues
    sources = set([])
    blacklist = set([])
    seen_URLs = set([])

    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mavik",
        database="Oven"
    )

    def __init__(self):
        self.parse_sources("Data/FirehoseSources.txt")
        self.parse_blacklist("Data/Blacklist.txt")
        self.LoadURLBlacklist()

    def LoadURLBlacklist(self):
        try:
            # Initialize the cursor
            cursor = self.db.cursor()

            # Execute the SQL command to select URLs
            cursor.execute("SELECT URL FROM URL_BLACKLIST;")

            # Fetch all the results
            results = cursor.fetchall()

            # Convert the results (a list of tuples) into a set of URLs
            self.seen_URLs = set(url[0] for url in results)

            # Print the number of loaded URLs
            print(f"Loaded {len(self.seen_URLs)} blacklisted URLs")

        except mysql.connector.Error as err:
            # Handle any errors that occur
            print(f"Error: {err}")
        finally:
            # Ensure the cursor is closed after operation
            cursor.close()

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
                        'Summary': getattr(entry, 'summary', 'No summary available')}

                    if filter:
                        age = datetime.now(timezone.utc) - entry_data['Published']  # Calc article age

                        # Check we haven't tried to read this URL before
                        if self.seen_URLs.__contains__(entry_data["URL"]):
                            self.already_done += 1
                            print(f"Skipping {entry_data['Title']} since it's already been viewed.")
                        else:
                            self.seen_URLs.add(entry_data["URL"])
                            if age <= timedelta(days=2):  # Ignore article if it's older than 2 days.
                                if (entry_data["Summary"] == "No summary available"):
                                    verdict = "Unknown"
                                else:
                                    # Filter based on phi-2 seeing if article is related to buisness.
                                    verdict = self.summary_filter(entry_data["Title"], entry_data["Summary"])
                                if verdict == "True" or verdict == "Unknown":
                                    entry_data['Content'] = self.get_article_text(entry_data["URL"])  # Get Article

                                    # Display information
                                    print(f"Found Story from {feed.feed.title} ({round(age.total_seconds() / 60 / 60, 2)} hrs ago) - {entry_data['Title']}")
                                    print(f"\t\t\t\t Article Text - {entry_data['Summary']}")
                                    self.Affected_Companies(entry_data["Title"], entry_data["Content"])
                                    entries_list.append(entry_data)
                                else:
                                    print(f"Skipping {entry_data['Title']} due to being irrelevant")
                                    self.LLMFilter += 1
                            else:
                                self.too_old += 1
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

    def summary_filter(self, Title, RSSSummary):
        Messages = [
            {"role": "system", "content": """You are given story headlines and summaries.
Your task is to determine if they are related to companies or not.
You should return your answers with either a Yes or No."""},
        {"role": "user", "content": f"Title:{Title}\nSSummary:{RSSSummary}"}]
        completion = client.chat.completions.create(model="local-model", messages=Messages, temperature=0.1,
                max_tokens=1).choices[0].message.content.lower().strip().translate(str.maketrans('', '', string.punctuation)).split(" ")[0]
        print(completion)
        if completion == "yes" or completion == "true":
            return "True"
        elif completion == "no" or completion == "false":
            return "False"
        else:
            return "Unknown"

    def Affected_Companies(self, Title, Article_Text):
        msgs = [
            {"role": "system", "content":
            """You identify companies in news articles.
            List companies affected line by line
            Only output a list of company names.
            Do not give any summary or context"""},
            {"role": "user", "content": f"Title:{Title}\nSSummary:{Article_Text}"}]

        completion = client.chat.completions.create(model="local-model", messages=msgs, temperature=0.1,max_tokens=10).choices[0].message
        print(completion)
        return completion



    def UpdateBlacklist(self):
        try:
            # Prepare a list of tuples from the set of URLs
            url_tuples = [(url,) for url in self.seen_URLs]

            # Execute the SQL command
            self.db.cursor().executemany("INSERT INTO URL_BLACKLIST (URL) VALUES (%s) ON DUPLICATE KEY UPDATE URL=URL;",
                                         url_tuples)

            # Commit your changes in the database
            self.db.commit()
        except mysql.connector.Error as err:
            # Handle errors such as duplicate entry
            print(f"Error: {err}")
            self.db.rollback()


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
            Blacklisted URL hits: {H.already_done} 
            Irrelevant: {H.LLMFilter}
            
            Updating URL Blacklist...""")
    H.UpdateBlacklist()
    print("Blacklist updated")
