import json

import requests_html
from bs4 import BeautifulSoup

from tickerlib import *


def _site_scraper_(site):
    # load website so all contents can be scraped
    tables = pandas.read_html(requests.get(site, headers=default_headers).text)
    _data = {}
    for table in tables:
        for value in table.values:
            _data.update({value[0]: str(value[1:])[2:-2]})

    return _data


def table_to_dict(table):
    _data = {}
    for value in table.values:
        _data.update({value[0]: [x for x in value[1:]]})

    return _data


def get_ticker_data(ticker):
    # Scrapes data elements found on Yahoo Finance's quote page
    site = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}"
    return _site_scraper_(site)


def get_ticker_stats(ticker):
    # Scrapes information from the statistics page on Yahoo Finance
    stats_site = f"https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}"
    ticker_stats = _site_scraper_(stats_site)
    if "Previous Close" in ticker_stats.keys():
        print("Ticker doesnt have stats")
        return {}
    else:
        return ticker_stats


# todo this function does the same as t_object.institutional_holders,
#  t_object.major_holders, t_object.mutualfund_holders
def get_holders(ticker):
    # Scrapes the Holders page from Yahoo Finance for an input ticker
    holders_site = f"https://finance.yahoo.com/quote/{ticker}/holders?p={ticker}"
    tables = pandas.read_html(requests.get(holders_site, headers=default_headers).text)
    table_names = ["Major Holders", "Direct Holders (Forms 3 and 4)",
                   "Top Institutional Holders", "Top Mutual Fund Holders"]
    table_mapper = {key: val for key, val in zip(table_names, tables)}

    return table_mapper


def get_analysts_info(ticker):
    # Scrapes the Analysts page from Yahoo Finance for an input ticker
    analysts_site = f"https://finance.yahoo.com/quote/{ticker}/analysts?p={ticker}"
    tables = pandas.read_html(requests.get(analysts_site, headers=default_headers).text)
    table_names = [table.columns[0] for table in tables]
    table_mapper = {key: val for key, val in zip(table_names, tables)}

    return table_mapper


def _force_float_(elt):
    try:
        return float(elt)
    except ValueError:
        return elt


def _convert_to_numeric_(s):
    if isinstance(s, float):
        return s

    if "M" in s:
        s = s.strip("M")
        return _force_float_(s) * 1_000_000

    if "B" in s:
        s = s.strip("B")
        return _force_float_(s) * 1_000_000_000

    return _force_float_(s)


def __raw_get_daily_info__(site, uk=False):
    session = requests_html.HTMLSession()
    resp = session.get(site)
    tables = pandas.read_html(resp.html.raw_html)
    df = tables[0].copy()
    df.columns = tables[0].columns

    if uk:
        del df["52-week range"]
        df["% change"] = df["% change"].map(lambda x: float(x.strip("%").replace(",", "")))
        fields_to_change = [x for x in df.columns.tolist() if "Vol" in x or x == "Market cap"]
    else:
        del df["52 Week Range"]
        df["% Change"] = df["% Change"].map(lambda x: float(x.strip("%+").replace(",", "")))
        fields_to_change = [x for x in df.columns.tolist() if "Vol" in x or x == "Market Cap"]

    for field in fields_to_change:
        if type(df[field][0]) == str:
            df[field] = df[field].map(_convert_to_numeric_)

    session.close()

    return table_to_dict(df)


def get_day_most_active_us(offset: int = 0, count: int = 100):
    return __raw_get_daily_info__(f"https://finance.yahoo.com/most-active?offset={offset}&count={count}")


def get_day_most_active_uk(offset: int = 0, count: int = 100):
    return __raw_get_daily_info__(f"https://uk.finance.yahoo.com/most-active?offset={offset}&count={count}", True)


def get_day_gainers_us(count: int = 100):
    return __raw_get_daily_info__(f"https://finance.yahoo.com/gainers?offset=0&count={count}")


def get_day_gainers_uk(count: int = 100):
    return __raw_get_daily_info__(f"https://uk.finance.yahoo.com/gainers?offset=0&count={count}", True)


def get_day_losers_us(count: int = 100):
    return __raw_get_daily_info__(f"https://finance.yahoo.com/losers?offset=0&count={count}")


def get_day_losers_uk(count: int = 100):
    return __raw_get_daily_info__(f"https://uk.finance.yahoo.com/losers?offset=0&count={count}", True)


def get_day_trending_tickers():
    return __raw_get_daily_info__(f"https://finance.yahoo.com/trending-tickers")


def get_day_top_etfs_us(count: int = 100):
    return __raw_get_daily_info__(f"https://finance.yahoo.com/etfs?offset=0&count={count}")


def get_day_top_etfs_uk(count: int = 100):
    return __raw_get_daily_info__(f"https://uk.finance.yahoo.com/etfs?offset=0&count={count}", True)


def get_day_top_mutual_us(count: int = 100):
    return __raw_get_daily_info__(f"https://finance.yahoo.com/mutualfunds?offset=0&count={count}")


def get_day_top_mutual_uk(count: int = 100):
    return __raw_get_daily_info__(f"https://uk.finance.yahoo.com/mutualfunds?offset=0&count={count}", True)


def get_day_top_futures():
    # why is there an unnamed column???
    return pandas.read_html(requests.get("https://finance.yahoo.com/commodities", headers=default_headers).text)[0]


def get_day_highest_open_interest(count: int = 100):
    # uses a different table format than other daily infos
    return pandas.read_html(requests.get(f"https://finance.yahoo.com/options/highest-open-interest?"
                                         f"offset=0&count={count}", headers=default_headers).text)[0]


def get_day_highest_implied_volatility(count: int = 100):
    # uses a different table format than other daily infos
    return pandas.read_html(requests.get(f"https://finance.yahoo.com/options/highest-implied-volatility?"
                                         f"offset=0&count={count}", headers=default_headers).text)[0]


def get_day_top_world_indices():
    return __raw_get_daily_info__(f"https://finance.yahoo.com/world-indices")


def get_day_top_forex_rates():
    return __raw_get_daily_info__(f"https://finance.yahoo.com/currencies")


def get_day_top_us_bonds():
    return __raw_get_daily_info__(f"https://finance.yahoo.com/bonds")


def get_day_top_crypto(offset: int = 0, count: int = 100):
    # Gets the top 100 Cryptocurrencies by Market Cap
    session = requests_html.HTMLSession()
    resp = session.get(f"https://finance.yahoo.com/cryptocurrencies?offset={offset}&count={count}")
    df = pandas.read_html(resp.html.raw_html)[0].copy()
    df["% Change"] = df["% Change"].map(lambda x: float(str(x).strip("%").strip("+").replace(",", "")))
    del df["52 Week Range"]
    del df["Day Chart"]

    fields_to_change = [x for x in df.columns.tolist() if "Volume" in x \
                        or x == "Market Cap" or x == "Circulating Supply"]

    for field in fields_to_change:
        if type(df[field][0]) == str:
            df[field] = df[field].map(lambda x: _convert_to_numeric_(str(x)))

    session.close()

    return df


# TODO lewis function not done
def get_bank_of_england_news():
    endResult = []
    soup = BeautifulSoup(requests.get("https://uk.finance.yahoo.com/topic/bank-of-england/", headers=default_headers).text, 'html.parser')
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


# TODO lewis function not done
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


### Earnings functions
def _parse_earnings_json(url):
    resp = requests.get(url, headers=default_headers)
    content = resp.content.decode(encoding='utf-8', errors='strict')
    page_data = [row for row in content.split('\n') if row.startswith('root.App.main = ')][0][:-1]
    page_data = page_data.split('root.App.main = ', 1)[1]

    return json.loads(page_data)


def get_earnings_history(ticker):
    # Returns the earnings calendar history of the input ticker with EPS actual vs. expected data.'''
    url = f"https://finance.yahoo.com/calendar/earnings?symbol={ticker}"
    return pandas.read_html(requests.get(url, headers=default_headers).text)[0]


# todo does not scrap LSE, check against yf.Ticker(ticker).get_earnings()
def get_earnings_for_date(date, offset=0, count=100):
    # TODO LIMITATION ONLY SHOWS REGION US
    # Returns a dictionary of stock tickers with earnings expected on the input date.
    # The dictionary contains the expected EPS values for each stock if available.
    date = pandas.Timestamp(date).strftime("%Y-%m-%d")
    url = f"https://finance.yahoo.com/calendar/earnings?day={date}&offset={offset}&size={count}"
    # https://query2.finance.yahoo.com/v1/finance/trending/US?count=50&useQuotes=true&fields=logoUrl%2CregularMarketChangePercent

    return pandas.read_html(requests.get(url, headers=default_headers).text)[0]


def get_earnings_in_date_range(start_date, end_date):

        '''Inputs: @start_date
                   @end_date
                   
           Returns the stock tickers with expected EPS data for all dates in the
           input range (inclusive of the start_date and end_date.'''

        earnings_data = []

        days_diff = pandas.Timestamp(end_date)- pandas.Timestamp(start_date)
        days_diff = days_diff.days
        current_date = pandas.Timestamp(start_date)

        dates = [current_date+datetime.timedelta(diff) for diff in range(days_diff + 1)]
        dates = [d.strftime("%Y-%m-%d") for d in dates]

        i = 0
        while i < len(dates):
            try:
                earnings_data += get_earnings_for_date(dates[i])
            except Exception:
                pass

            i += 1

        return earnings_data


def get_currencies():
    # Returns the currencies table from Yahoo Finance
    site = "https://finance.yahoo.com/currencies"
    return pandas.read_html(requests.get(site, headers=default_headers).text)[0]


def get_futures():
    # Returns the futures table from Yahoo Finance
    site = "https://finance.yahoo.com/commodities"
    return pandas.read_html(requests.get(site, headers=default_headers).text)[0]


def get_undervalued_large_caps(offset: int = 0, count: int = 100):  # todo NOT POSSIBLE TO SCRAPE REGIONS OTHER THAN US
    # Returns the undervalued large caps table from Yahoo Finance
    site = "https://finance.yahoo.com/screener/predefined/undervalued_large_caps?offset={offset}&count={count}"
    return pandas.read_html(requests.get(site, headers=default_headers).text)[0]


# extra TNS code to try to detect if invalid ticker is returned from TNS and fix ticker
# code also returns ticker data
def tns_check(ticker, name):
    ticker_live = get_ticker_data(ticker)
    fixed = True
    try:
        ticker_live['Open']
    except KeyError:
        fixed = False
    for key in ticker_live.keys():
        if re.search(r"\b"+re.escape(name.lower())+r"\b", ticker_live[key].lower()):
            print(f"TNS Check fixed: {ticker[0][0]} --> {key}")
            ticker = [[key, ticker_live[key]]]
            ticker_live = get_ticker_data(ticker[0][0])
            fixed = True
            break
    if not fixed:
        print(ticker_live)
        exit(f"Ticker error: TNS Check failed to resolve ticker")
    return ticker_live


class TNS:
    def __init__(self, c_list, search_all=False):
        self.tickers = tns(c_list, search_all)
        if not self.tickers:
            print("Ticker not found: TNS failed to resolve ticker(s)")

    def get_objects(self):
        ticker_objects = {}
        for key in self.tickers.keys():
            ticker_objects.update({key: Ticker(key)})
        return ticker_objects

    def get_results(self):
        return self.tickers


class Ticker:
    def __init__(self, ticker):
        self.ticker_obj = yfinance.Ticker(ticker)
        self.profile = None

    def get_profile(self):
        if self.profile:
            return self.profile
        else:
            self.profile = load_ticker_info(self.ticker_obj.ticker)
            return self.profile

    def get_news(self):
        return self.ticker_obj.news
