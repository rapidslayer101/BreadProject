from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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


class NewsScraper:
    def __init__(self):
        self.browser = webdriver.Chrome()
        pass

    def scrape_site_for_links(self, site_url: str, scroll_time: int):
        self.browser.get(site_url)
        time.sleep(1)
        while scroll_time > 0:
            self.browser.find_element(By.XPATH, "//body").send_keys(Keys.END)
            time.sleep(1)
            scroll_time -= 1

        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        links = soup.find_all("a")

        # Get links
        for a_tag in links:
            try:
                print(a_tag["href"])
            except KeyError:
                print("Fail")
        pass

    def close(self):
        self.browser.quit()
    pass


class YahooFinanceNewsScraper(NewsScraper):
    acceptedConsent = False

    def __init__(self):
        super().__init__()

    def accept_consent_cookies(self, site_url: str):
        self.browser.get(site_url)
        time.sleep(1)
        self.browser.find_element(By.XPATH, "//button[@value='agree']").click()
        self.acceptedConsent = True

    def scrape_site_for_links(self, site_url: str, scroll_time: float):
        if not self.acceptedConsent:
            self.accept_consent_cookies(site_url)

        super().scrape_site_for_links(site_url, scroll_time)

    pass


cnn = NewsScraper()
cnn.scrape_site_for_links("https://edition.cnn.com/", 5)
cnn.close()
# yahoo = YahooFinanceNewsScraper()
# yahoo.scrape_site_for_links("https://uk.finance.yahoo.com/topic/bank-of-england/", 5)
# yahoo.close()


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