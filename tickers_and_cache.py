import json
import requests_html
from tickerlib import *

# This file contains functions that scrape data from Yahoo Finance
# This file should be called when the program starts


def table_to_dict(table):
    _data = {}
    for value in table.values:
        _data.update({value[0]: [x for x in value[1:] if str(x) not in ["", "-"]]})

    return _data


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
        if isinstance(df[field][0], str):
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


def get_day_top_futures_us():
    # why is there an unnamed column???
    return pandas.read_html(requests.get("https://finance.yahoo.com/commodities", headers=default_headers).text)[0]


def get_day_top_futures_uk():
    # why is there an unnamed column???
    return pandas.read_html(requests.get("https://uk.finance.yahoo.com/commodities", headers=default_headers).text)[0]


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

    fields_to_change = [x for x in df.columns.tolist() if "Volume" in x
                        or x == "Market Cap" or x == "Circulating Supply"]

    for field in fields_to_change:
        if isinstance(df[field][0], str):
            df[field] = df[field].map(lambda x: _convert_to_numeric_(str(x)))

    session.close()

    return df


# Earnings functions
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


def get_earnings_for_date_us(date=datetime.datetime.today(), offset=0, count=100):
    # Returns a dictionary of stock tickers with earnings expected on the input date.
    # The dictionary contains the expected EPS values for each stock if available.
    date = pandas.Timestamp(date).strftime("%Y-%m-%d")
    url = f"https://finance.yahoo.com/calendar/earnings?day={date}&offset={offset}&size={count}"

    return table_to_dict(pandas.read_html(requests.get(url, headers=default_headers).text)[0])


def get_earnings_for_date_uk(date=datetime.datetime.today(), offset=0, count=100):
    # Returns a dictionary of stock tickers with earnings expected on the input date.
    # The dictionary contains the expected EPS values for each stock if available.
    date = pandas.Timestamp(date).strftime("%Y-%m-%d")
    url = f"https://uk.finance.yahoo.com/calendar/earnings?day={date}&offset={offset}&size={count}"

    return table_to_dict(pandas.read_html(requests.get(url, headers=default_headers).text)[0])


# todo test and fix function
def _get_earnings_in_date_(start_date, end_date, market):
    # Returns the stock tickers with expected EPS data for all dates in the input range
    earnings_data = {}
    days_diff = pandas.Timestamp(end_date)-pandas.Timestamp(start_date).days
    dates = [pandas.Timestamp(start_date)+datetime.timedelta(diff) for diff in range(days_diff+1)]

    for date in dates:
        try:
            if market == "uk":
                earnings_data.update({date: get_earnings_for_date_uk(date)})
            elif market == "us":
                earnings_data.update({date: get_earnings_for_date_us(date)})
        except Exception:
            pass

    return earnings_data


# todo test and fix function
def get_earnings_in_date_range_us(start_date, end_date):
    return _get_earnings_in_date_(start_date, end_date, "us")


# todo test and fix function
def get_earnings_in_date_range_uk(start_date, end_date):
    return _get_earnings_in_date_(start_date, end_date, "uk")


def get_currencies():
    # Returns the currencies table from Yahoo Finance
    site = "https://finance.yahoo.com/currencies"
    return pandas.read_html(requests.get(site, headers=default_headers).text)[0]


def get_futures():
    # Returns the futures table from Yahoo Finance
    site = "https://finance.yahoo.com/commodities"
    return pandas.read_html(requests.get(site, headers=default_headers).text)[0]


def get_undervalued_large_caps_us(offset: int = 0, count: int = 100):
    # Returns the undervalued large caps table from Yahoo Finance
    site = f"https://finance.yahoo.com/screener/predefined/undervalued_large_caps?offset={offset}&count={count}"
    return pandas.read_html(requests.get(site, headers=default_headers).text)[0]


def get_undervalued_large_caps_uk(offset: int = 0, count: int = 100):
    # Returns the undervalued large caps table from Yahoo Finance
    site = f"https://uk.finance.yahoo.com/screener/predefined/undervalued_large_caps?offset={offset}&count={count}"
    return pandas.read_html(requests.get(site, headers=default_headers).text)[0]
