"""
       /\
      /  \
     /,--.\
    /< () >\
   /  `--'  \
  / IlloomAI \
 / HYDRANT.py \
/______________\
A mass media analysis tool
"""

import re
import time
from datetime import datetime, timedelta, timezone
import mysql.connector
import feedparser
import mysql
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dt_parse
from openai import OpenAI
import string
import tickers_and_cache as tnc

NOSQL = False  # If true, does not try anything with MySQL
NOLLM = False  # If true, does not try to use LLM
NOURLBLACKLIST = True  # The blacklist won't be loaded.
SHOWOUTDATEDARTICLES = False # articles older than 2 days won't be mentioned
if not NOLLM:
    client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed")

too_old = 0
errored_text = 0
errored_parsing = 0
already_done = 0
LLMFilter = 0
NotablePeopleHits = 0

# Sources is a set to prevent dupe issues
sources = set([])
seen_URLs = set([])

# Names of companies and their executives
Execs = dict([])
CompanyNames = set([])

if not NOSQL:
    db = mysql.connector.connect(host="localhost", user="root", password="Mavik", database="Oven")


def load_exec_data():
    """
    Gets ands parses company exec names
    """

    dat = ticker.get_exec_data()
    for key in dat.keys():
        for executive in dat[key]:
            Execs.update({strip_titles(executive["name"]): key})


def load_company_names():
    """
    Gets ands parses company names (long and short names)
    """
    dat = ticker.get_comp_names_l()
    dat.update(ticker.get_comp_names_s())
    for name in dat.values():
        CompanyNames.update(name)


def load_url_blacklist():
    global seen_URLs, db
    if NOSQL or NOURLBLACKLIST:
        seen_URLs = set()
    else:
        try:
            # Initialize the cursor
            cursor = db.cursor()

            # Execute the SQL command to select URLs
            cursor.execute("SELECT URL FROM URL_BLACKLIST;")

            # Fetch all the results
            results = cursor.fetchall()

            # Convert the results (a list of tuples) into a set of URLs
            seen_URLs = set(url[0] for url in results)

            # Print the number of loaded URLs
            print(f"Loaded {len(seen_URLs)} blacklisted URLs")

        except mysql.connector.Error as err:
            # Handle any errors that occur
            print(f"Error: {err}")


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


def get_relevant_stories():
    global errored_text, sources, blacklist, db, too_old, LLMFilter, already_done, errored_parsing, NotablePeopleHits
    NextStage = []  # Stories that are actually worth parsing
    for source in sources:
        feed = feedparser.parse(source)
        for entry in feed.entries:  # Loop through each entry in the feed
            try:
                # Don't do anything with the story if we have previously viewed it
                if entry.link in seen_URLs:
                    print(f"Already viewed {entry.title}")
                    already_done += 1
                    continue

                # Don't do anything with stories older than two days
                if datetime.now(timezone.utc) - dt_parse.parse(entry.published) <= timedelta(days=2):
                    if SHOWOUTDATEDARTICLES:
                        print(f"Skipping {entry.title} as it's older than two days.")
                    too_old += 1
                    continue

                # Create article dict
                article = {
                    'Title': entry.title, 'URL': entry.link, "Execs": [], "Companies": [],
                    'Published': dt_parse.parse(getattr(entry, "published", "updated")),
                    'Summary': getattr(entry, 'summary', "Summary unavailable"),
                    "Content": get_article_text(entry.link)}

                # Stories containing execs are worth parsing
                for executive in Execs.keys():
                    if executive in article["Content"]:
                        NotablePeopleHits += 1
                        article["Execs"].append(Execs.get(executive))

                # Stories containing companies are worth parsing
                for company in CompanyNames:
                    if company in article["Content"]:
                        article["Companies"].append(company)

                # Add the story to be summarised if it is about an exec/company if we don't have an RSS summary
                if (len(article["Companies"]) > 1 or len(article["Execs"]) > 0 or
                        article["Summary"] == "Summary unavailable"):
                    NextStage.append(article)
                    print(f"[NEW] {article['Title']} - Execs: {len(article['Execs'])} | Companies: {len(CompanyNames)}"
                          f"\t\t\t{article['Summary']}")
                    summarise(article["Title"], article["Content"])
                else:
                    worth_reading = summary_filter(article["Title"], article["Summary"])
                    if worth_reading == "True" or worth_reading == "Unknown":
                        summarise(article["Title"], article["Content"])
                        NextStage.append(article)

            except Exception as ex:
                errored_parsing += 1
                print(f"ERROR:{ex}")

    return NextStage

def test_strings():
    file = open(f"HydrantData/Test/TestRun.txt", "a+", encoding="utf-8")
    for source in sources:
        src = (feedparser.parse(source)).entries
        if len(src) != 0:
            file.writelines(f"source\n\n\n====={get_article_text(src[0]['link'])}")
    file.close()
    return

def summarise(Headline, Content):
    messages = [
        {"role": "system", "content": """Instruction: Your task is to give a short yet effective summary of the given 
        stories. Your summaries should be roughly a paragraph long and not much longer. Your summaries should 
        encapsulate all relevant content within the article. Your titles should not include article titles, your outputs
        only need to include summaries."""},
        {"role": "user", "content": f"Title: {Headline}\n{Content}"}]
    completion = client.chat.completions.create(model="lunatic", messages=messages, temperature=0.2, max_tokens=400)
    msg = completion.choices[0].message.content.strip()
    print(msg)


def strip_titles(text):
    """
    This strips titles from names such as Mr.
    """
    # TODO: add foreign titles
    # List of titles to remove
    titles = ['Mr.', 'Mrs.', 'Miss', 'Ms.', 'Dr.', 'Prof.', 'Sir', 'Dame', 'Lord', 'Lady', 'Rev.', 'Hon.',
              'Sgt.', 'Capt.', 'Cllr.']

    # Create a regular expression pattern
    pattern = r'\b(?:' + '|'.join(titles) + r')\b'

    # Use regex to replace titles with an empty string
    return re.sub(pattern, '', text)


def find_people_of_interest(text):
    global NotablePeopleHits
    for executive in Execs.keys():
        if executive in text:
            NotablePeopleHits += 1
            CompanyNames.add(Execs[executive])
            print("Found " + executive + " in article")


def summary_filter(title, rss_summary):
    if NOLLM:
        return "Unknown"

    messages = [
        {"role": "system", "content": """You are given story headlines and summaries.
Your task is to determine if they are related to companies, poltics or geoplotics.
You should return your answers with either a Yes or No."""},
        {"role": "user", "content": f"Title:{title}\nSummary:{rss_summary}"}]
    completion = client.chat.completions.create(model="llama", messages=messages, temperature=0.1,
                                                max_tokens=1).choices[0].message.content.lower().strip().translate(
        str.maketrans('', '', string.punctuation)).split(" ")[0]
    if completion == "yes" or completion == "true":
        return "True"
    elif completion == "no" or completion == "false":
        return "False"
    else:
        return "Unknown"


def update_blacklist():
    if NOSQL:
        print("Not updating blacklist since NOSQL is true.")
        return
    try:
        # Prepare a list of tuples from the set of URLs
        url_tuples = [(url,) for url in seen_URLs]

        # Execute the SQL command
        db.cursor().executemany("INSERT INTO URL_BLACKLIST (URL) VALUES (%s) ON DUPLICATE KEY UPDATE URL=URL;",
                                url_tuples)

        # Commit your changes in the database
        db.commit()
    except mysql.connector.Error as err:
        # Handle errors such as duplicate entry
        print(f"Error: {err}")
        db.rollback()

start = time.time()
parse_sources("HydrantData/FirehoseSources.txt")
parse_blacklist("HydrantData/Blacklist.txt")
#test_strings()
load_url_blacklist()
object_ = tnc.TNS("Tesco").get_objects()
print(object_)
#load_company_names()
res = get_relevant_stories()
print(f"""Stats
    Took {round((time.time() - start), 2)}s
    Ready: {len(res)}
    Too Old: {too_old}
    Article Parsing Errors: {errored_parsing}
    Errors text: {errored_text}
    URL Blacklist Size: {len(seen_URLs)}
    Blacklisted URL hits: {already_done} 
    Irrelevant Articles: {LLMFilter}
    Notable People found in articles: {NotablePeopleHits}
    Executives: {len(Execs)}
    Company Aliases: {len(CompanyNames)}""")
update_blacklist()
print("Blacklist updated")
