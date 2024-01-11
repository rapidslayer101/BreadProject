from selenium import webdriver
import time
from bs4 import BeautifulSoup
import requests

# this file is a test file and notes file on news scraping

# todo for lewis (unfinished list of all feeds on uk.finance.yahoo.com)
# scrape https://uk.finance.yahoo.com/
# scrape https://uk.finance.yahoo.com/topic/news/
# scrape https://uk.finance.yahoo.com/calendar
# scrape https://uk.finance.yahoo.com/world-indices/
# scrape https://uk.finance.yahoo.com/currencies/
# scrape https://uk.finance.yahoo.com/crypto/
# scrape https://uk.finance.yahoo.com/topic/bank-of-england/
# scrape https://uk.finance.yahoo.com/topic/saving-spending/
# scrape https://uk.finance.yahoo.com/topic/small-business/
# scrape https://uk.finance.yahoo.com/topic/property/
# scrape https://uk.yahoo.com/topics/ipo-watch/
# scrape https://uk.finance.yahoo.com/work-management/
# scrape https://uk.finance.yahoo.com/industries/autos_transportation/  # could include table

# todo look at finance.yahoo.com/ and see if there is anything else that could be scraped


# todo realisation could make a webcrawler and webscraper, detects all news on a page, checks uniqueness (0,1)
# todo then checks if the news is relevant with AI
# todo then appends link to list to be reviewed by a human
# todo finally we have big long list of news websites that we can use in hydrant


# https://stackoverflow.com/questions/22702277/crawl-site-that-has-infinite-scrolling-using-python
# https://stackoverflow.com/questions/69046183/how-do-i-scrape-a-website-with-an-infinite-scroller
# https://csnotes.medium.com/web-scraping-infinite-scrolling-with-selenium-97f820d2e506
# https://duckduckgo.com/?q=python+how+to+webscrape+an+infinite+scroll+webpage&atb=v338-1&ia=web

default_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/120.0.0.0 Safari/537.3'}


# open browser and scrape

browser = webdriver.Chrome()
browser.get("https://uk.finance.yahoo.com/topic/bank-of-england/")
# scroll to bottom of page
browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# wait for page to load
time.sleep(5)
# get html
html = browser.page_source
# close browser
browser.quit()

# parse html
soup = BeautifulSoup(html, "html.parser")
# find all news articles
news_articles = soup.find_all("div", class_="Mb(5px)")


# TODO lewis old functions
def get_bank_of_england_news():
    endResult = []
    soup = BeautifulSoup(requests.get("https://uk.finance.yahoo.com/topic/bank-of-england/", headers=default_headers).text, 'html.parser')
    print(soup)
    uL = soup.find("ul", {'class': 'My(0) P(0) Wow(bw) Ov(h)'})
    articles = uL.find_all("li")
    for article in articles:
        # adblock LMAO
        if article.find("div", {"class": "native-ad-item"}) != None:
            continue
        articleDiv = article.find("div").find("div").find_all("div")[2]
        titleDiv = articleDiv.find("h3").find("a")
        link = titleDiv["href"]
        title = titleDiv.text
        desc = articleDiv.find("p").text
        result = [title, desc, f"https://uk.finance.yahoo.com{str(link)}"]
        endResult.append(result)
    print(endResult)


# TODO lewis old functions
def get_saving_spending_news():
    endResult = []
    soup = BeautifulSoup(
        requests.get("https://uk.finance.yahoo.com/topic/saving-spending/", headers=default_headers).text,
        'html.parser')
    uL = soup.find("ul", {'class': 'My(0) P(0) Wow(bw) Ov(h)'})
    articles = uL.find_all("li")
    for article in articles:
        # adblock LMAO
        if article.find("div", {"class": "native-ad-item"}) != None:
            continue
        articleDiv = article.find("div").find("div").find_all("div")[2]
        titleDiv = articleDiv.find("h3").find("a")
        link = titleDiv["href"]
        title = titleDiv.text
        desc = articleDiv.find("p").text
        result = [title, desc, f"https://uk.finance.yahoo.com{str(link)}"]
        endResult.append(result)
    print(endResult)