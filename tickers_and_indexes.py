import requests
import pandas as pd
import ftplib
import io
import re
import json
import datetime
import warnings
from os import rename, mkdir
from os.path import exists
from datetime import datetime, timedelta
from pandas import read_excel


# file of functions to pull tickers and indexes from various sources
# MODIFIED FROM YAHOO-FIN LIBRARY AT: https://pypi.org/project/yahoo-fin/#history

if not exists("TickerData"):
    mkdir("TickerData")
    print("Created TickerData directory...")
else:
    print("Found TickerData directory...")

if not exists("TickerData/Tickers"):
    mkdir("TickerData/Tickers")

warnings.simplefilter(action='ignore', category=FutureWarning)
default_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/120.0.0.0 Safari/537.3'}


try:
    from requests_html import HTMLSession
except Exception:
    print("""Warning - Certain functionality 
             requires requests_html, which is not installed.
             
             Install using: 
             pip install requests_html
             
             After installation, you may have to restart your Python session.""")

    
base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"


def build_url(ticker, start_date=None, end_date=None, interval="1d"):
    
    if end_date is None:  
        end_seconds = int(pd.Timestamp("now").timestamp())
    else:
        end_seconds = int(pd.Timestamp(end_date).timestamp())
        
    if start_date is None:
        start_seconds = 7223400
    else:
        start_seconds = int(pd.Timestamp(start_date).timestamp())
    
    site = base_url + ticker
    
    params = {"period1": start_seconds, "period2": end_seconds,
              "interval": interval.lower(), "events": "div,splits"}

    return site, params


def force_float(elt):
    try:
        return float(elt)
    except ValueError:
        return elt


def _convert_to_numeric(s):
    if isinstance(s, float):
        return s

    if "M" in s:
        s = s.strip("M")
        return force_float(s) * 1_000_000
    
    if "B" in s:
        s = s.strip("B")
        return force_float(s) * 1_000_000_000

    return force_float(s)


def tickers_sp500():  # Downloads list of tickers currently listed in the S&P 500
    sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    sp_tickers = []
    for i in range(len(sp500)):
        sp_tickers.append(f"{sp500.values[i][0]}§{sp500.values[i][1]}§{sp500.values[i][2]}§"
                          f" {sp500.values[i][3]}§{sp500.values[i][4]}§{sp500.values[i][6]}")

    return sp_tickers


def _nasdaq_trader(search_param):  # Downloads list of nasdaq tickers
    ftp = ftplib.FTP("ftp.nasdaqtrader.com")
    ftp.login()
    ftp.cwd("SymbolDirectory")

    r = io.BytesIO()
    ftp.retrbinary(f'RETR {search_param}.txt', r.write)

    info = r.getvalue().decode()
    splits = info.split("|")

    tickers = [x for x in splits if len(x) > 1]
    ticker_data = []
    for i in range(len(tickers)-4):
        if tickers[i] == "100" and "-" in tickers[i+2]:
            stock_ticker = tickers[i+1].split('\r\n')[1]
            stock_name = tickers[i+2].split(" - ")[0]
            stock_type = str(tickers[i+2].split(" - ")[1:])[2:-2]
            ticker_data.append(f"{stock_ticker}§{stock_name}§{stock_type}")
        elif tickers[i] == "100" and "-" not in tickers[i+2] and "test stock" not in tickers[i+2].lower():
            stock_ticker = tickers[i+1].split('\r\n')[1]
            ticker_data.append(f"{stock_ticker}§{tickers[i+2]}")

    return ticker_data


def tickers_nasdaq():  # Nasdaq stocks
    return _nasdaq_trader("nasdaqlisted")


def tickers_us_other():  # Nasdaq other, funds, etfs, etc.
    return _nasdaq_trader("otherlisted")
    

def tickers_dow():  # Dow_Jones_Industrial_Average
    site = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
    table = pd.read_html(site, attrs={"id": "constituents"})[0]
    dow_tickers = []
    for i in range(len(table)):
        dow_tickers.append(f"{table.values[i][2]}§{table.values[i][0]}§{table.values[i][6]}§{table.values[i][1]}§"
                           f"{table.values[i][3]}")

    return dow_tickers    


def tickers_nifty50():  # NIFTY 50, India
    site = "https://en.wikipedia.org/wiki/NIFTY_50"
    table = pd.read_html(site, attrs={"id": "constituents"})[0]
    nifty50 = []
    for i in range(len(table)):
        nifty50.append(f"{table.values[i][1]}§{table.values[i][0]}§{table.values[i][2]}")

    return nifty50


def tickers_ftse100():  # UK 100
    table = pd.read_html("https://en.wikipedia.org/wiki/FTSE_100_Index", attrs={"id": "constituents"})[0]
    ftse100 = []
    for i in range(len(table)):
        ftse100.append(f"{table.values[i][1]}.L§{table.values[i][0]}§{table.values[i][2]}")

    return ftse100
    

def tickers_ftse250():  # UK 250
    table = pd.read_html("https://en.wikipedia.org/wiki/FTSE_250_Index", attrs={"id": "constituents"})[0]
    ftse250 = []
    for i in range(len(table)):
        ftse250.append(f"{table.values[i][1]}.L§{table.values[i][0]}§{table.values[i][2]}")
    return ftse250


def _writer_(file, refresh_days):
    with open(f"TickerData/{file}.txt", "w", encoding="utf-8") as f:
        f.write(f"# reload+after+{datetime.now()+timedelta(days=refresh_days)}\n")
        if file == "sp_500":
            data = tickers_sp500()  #
        elif file == "nasdaq":
            data = tickers_nasdaq()
        elif file == "nasdaq_other":
            data = tickers_us_other()
        elif file == "dow_jones":
            data = tickers_dow()
        elif file == "nifty50":
            data = tickers_nifty50()
        elif file == "ftse100":
            data = tickers_ftse100()
        elif file == "ftse250":
            data = tickers_ftse250()

        ticker_info = []
        for ticker in data:
            f.write(f"{ticker}\n")
            ticker_info.append(ticker.split("§"))

    return ticker_info


def refresh_ticker_data(file, refresh_days):
    if not exists(f"TickerData/{file}.txt"):
        print(f"Downloading {file} tickers...")
        ticker_info = _writer_(file, refresh_days)
    else:
        with open(f"TickerData/{file}.txt", "r", encoding="utf-8") as f:
            file_time = datetime.strptime(f.readline().split("+")[2].replace("\n", ""), "%Y-%m-%d %H:%M:%S.%f")
            if file_time < datetime.now():
                ticker_info = _writer_(file, refresh_days)
                print(f"Found and refreshed {file} tickers...")
            else:
                print(f"Found {file} tickers...")
                ticker_info = []
                for ticker in f.readlines():
                    ticker_info.append(ticker.replace("\n", "").split("§"))
    return ticker_info


def _lse_writer_(data, file, refresh_days):
    with open(f"TickerData/{file}.txt", "w", encoding="utf-8") as f:
        f.write(f"# reload+after+{datetime.now()+timedelta(days=refresh_days)}\n")
        for ticker in data:
            line = ""
            for i in range(len(ticker)):
                if i == 0:
                    line += f"{ticker[i]}.L§"
                else:
                    line += f"{ticker[i]}§"
            f.write(f"{line[:-1]}\n")


def _lse_reader_():
    if not exists(f"TickerData/lse.xlsx"):
        print("LSE tickers not found, please download the file from "
              "https://www.londonstockexchange.com/reports?tab=instruments, then save it as lse.xlsx in the "
              "TickerData folder")
        exit()
    else:
        print(f"Downloading lse tickers...")
        data = read_excel(f"TickerData/lse.xlsx", None)
        all_eq = data['1.0 All Equity'].values.tolist()[8:]
        all_no_eq = data['2.0 All Non-Equity'].values.tolist()[8:]
        _lse_writer_(all_eq, "lse", 31)
        _lse_writer_(all_no_eq, "lse_eq", 31)
        rename("TickerData/lse.xlsx", "TickerData/lse_old.xlsx")
        return all_eq, all_no_eq


def refresh_lse_tickers():
    if not exists(f"TickerData/lse.txt") or not exists(f"TickerData/lse_eq.txt"):
        return _lse_reader_()
    else:
        with open(f"TickerData/lse.txt", "r", encoding="utf-8") as f:
            file_time = datetime.strptime(f.readline().split("+")[2].replace("\n", ""), "%Y-%m-%d %H:%M:%S.%f")
            if file_time < datetime.now():
                return _lse_reader_()
            else:
                print(f"Found lse and lse_eq tickers...")
                _lse = []
                for ticker in f.readlines():
                    _lse.append(ticker.replace("\n", "").split("§"))
                with open(f"TickerData/lse_eq.txt", "r", encoding="utf-8") as g:
                    _lse_eq = []
                    for ticker in g.readlines()[1:]:
                        _lse_eq.append(ticker.replace("\n", "").split("§"))
                return _lse, _lse_eq


def _site_scraper(site):
    # load website so all contents can be scraped
    tables = pd.read_html(requests.get(site, headers=default_headers).text)
    data = {}
    for table in tables:
        for value in table.values:
            data.update({value[0]: str(value[1:])[2:-2]})

    return data


def get_ticker_data(ticker):
    # Scrapes data elements found on Yahoo Finance's quote page
    site = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}"
    return _site_scraper(site)


def get_ticker_stats(ticker):
    # Scrapes information from the statistics tab on Yahoo Finance
    stats_site = f"https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}"
    return _site_scraper(stats_site)


# todo check which of below functions are useful
def _parse_json(url, headers=default_headers):
    html = requests.get(url=url, headers=headers).text
    json_str = html.split('root.App.main =')[1].split(
        '(this)')[0].split(';\n}')[0].strip()
    
    try:
        data = json.loads(json_str)[
            'context']['dispatcher']['stores']['QuoteSummaryStore']
    except:
        return '{}'
    else:
        # return data
        new_data = json.dumps(data).replace('{}', 'null')
        new_data = re.sub(r'\{[\'|\"]raw[\'|\"]:(.*?),(.*?)}', r'\1', new_data)

        json_info = json.loads(new_data)

        return json_info


# todo this function does the same as t_object.institutional_holders,
#  t_object.major_holders, t_object.mutualfund_holders
def get_holders(ticker, headers=default_headers):
    # Scrapes the Holders page from Yahoo Finance for an input ticker
    holders_site = f"https://finance.yahoo.com/quote/{ticker}/holders?p={ticker}"
    tables = pd.read_html(requests.get(holders_site, headers=headers).text)
    table_names = ["Major Holders", "Direct Holders (Forms 3 and 4)",
                   "Top Institutional Holders", "Top Mutual Fund Holders"]
    table_mapper = {key: val for key, val in zip(table_names, tables)}

    return table_mapper       


# todo provides 5 tables of unique data, check usefulness
def get_analysts_info(ticker, headers=default_headers):
    # Scrapes the Analysts page from Yahoo Finance for an input ticker
    analysts_site = f"https://finance.yahoo.com/quote/{ticker}/analysts?p={ticker}"
    tables = pd.read_html(requests.get(analysts_site, headers=headers).text)
    table_names = [table.columns[0] for table in tables]
    table_mapper = {key: val for key, val in zip(table_names, tables)}

    return table_mapper


# todo check usefulness, it still works at least
def _raw_get_daily_info(site):
    session = HTMLSession()
    resp = session.get(site)
    tables = pd.read_html(resp.html.raw_html)
    df = tables[0].copy()
    df.columns = tables[0].columns
    del df["52 Week Range"]
    df["% Change"] = df["% Change"].map(lambda x: float(x.strip("%+").replace(",", "")))
    fields_to_change = [x for x in df.columns.tolist() if "Vol" in x or x == "Market Cap"]
    
    for field in fields_to_change:

        if type(df[field][0]) == str:
            df[field] = df[field].map(_convert_to_numeric)
            
    session.close()
    
    return df
    

def get_day_most_active(count: int=100):
    return _raw_get_daily_info(f"https://finance.yahoo.com/most-active?offset=0&count={count}")


def get_day_gainers(count: int=100):
    return _raw_get_daily_info(f"https://finance.yahoo.com/gainers?offset=0&count={count}")


def get_day_losers(count: int=100):
    return _raw_get_daily_info(f"https://finance.yahoo.com/losers?offset=0&count={count}")


def get_day_trending_tickers():
    return _raw_get_daily_info(f"https://finance.yahoo.com/trending-tickers")


def get_day_top_etfs(count: int=100):
    return _raw_get_daily_info(f"https://finance.yahoo.com/etfs?offset=0&count={count}")


def get_day_top_mutual(count: int=100):
    return _raw_get_daily_info(f"https://finance.yahoo.com/mutualfunds?offset=0&count={count}")


def get_day_top_futures(headers=default_headers):
    # why is there a unnamed column???
    return pd.read_html(requests.get("https://finance.yahoo.com/commodities", headers=headers).text)[0]


def get_day_highest_open_interest(count: int=100, headers=default_headers):
    # uses a different table format than other daily infos
    return pd.read_html(requests.get(f"https://finance.yahoo.com/options/highest-open-interest?offset=0&count={count}", headers=headers).text)[0]


def get_day_highest_implied_volatility(count: int=100, headers=default_headers):
    # uses a different table format than other daily infos
    return pd.read_html(requests.get(f"https://finance.yahoo.com/options/highest-implied-volatility?offset=0&count={count}", headers=headers).text)[0]


def get_day_top_world_indices():
    return _raw_get_daily_info(f"https://finance.yahoo.com/world-indices")


def get_day_top_forex_rates():
    return _raw_get_daily_info(f"https://finance.yahoo.com/currencies")


def get_day_top_us_bonds():
    return _raw_get_daily_info(f"https://finance.yahoo.com/bonds")


def get_day_top_crypto():
    # Gets the top 100 Cryptocurrencies by Market Cap
    session = HTMLSession()
    resp = session.get("https://finance.yahoo.com/cryptocurrencies?offset=0&count=100")
    df = pd.read_html(resp.html.raw_html)[0].copy()
    df["% Change"] = df["% Change"].map(lambda x: float(str(x).strip("%").strip("+").replace(",", "")))
    del df["52 Week Range"]
    del df["Day Chart"]
    
    fields_to_change = [x for x in df.columns.tolist() if "Volume" in x \
                        or x == "Market Cap" or x == "Circulating Supply"]
    
    for field in fields_to_change:
        if type(df[field][0]) == str:
            df[field] = df[field].map(lambda x: _convert_to_numeric(str(x)))

    session.close()        
                
    return df
        


### Earnings functions
def _parse_earnings_json(url, headers=default_headers):
        resp = requests.get(url, headers=headers)
        
        content = resp.content.decode(encoding='utf-8', errors='strict')
        
        page_data = [row for row in content.split(
            '\n') if row.startswith('root.App.main = ')][0][:-1]
        
        page_data = page_data.split('root.App.main = ', 1)[1]
        
        return json.loads(page_data)


def get_earnings_history(ticker):
    # Returns the earnings calendar history of the input ticker with EPS actual vs. expected data.'''
    url = f"https://finance.yahoo.com/calendar/earnings?symbol={ticker}"
    return pd.read_html(requests.get(url, headers=default_headers).text)[0]


# todo does not scrap LSE, check against yf.Ticker(ticker).get_earnings()
def get_earnings_for_date(date, offset=0, count=1):

    '''Inputs: @date
       Returns a dictionary of stock tickers with earnings expected on the
       input date.  The dictionary contains the expected EPS values for each
       stock if available.'''
    
    base_earnings_url = 'https://finance.yahoo.com/calendar/earnings'
    
    if offset >= count:
        return []
    
    temp = pd.Timestamp(date)
    date = temp.strftime("%Y-%m-%d")

    dated_url = '{0}?day={1}&offset={2}&size={3}'.format(base_earnings_url, date, offset, 100)
    
    result = _parse_earnings_json(dated_url)
    
    stores = result['context']['dispatcher']['stores']
    
    earnings_count = stores['ScreenerCriteriaStore']['meta']['total']

    new_offset = offset + 100
    
    more_earnings = get_earnings_for_date(date, new_offset, earnings_count)
    
    current_earnings = stores['ScreenerResultsStore']['results']['rows']

    total_earnings = current_earnings + more_earnings

    return total_earnings


def get_earnings_in_date_range(start_date, end_date):

        '''Inputs: @start_date
                   @end_date
                   
           Returns the stock tickers with expected EPS data for all dates in the
           input range (inclusive of the start_date and end_date.'''
    
        earnings_data = []

        days_diff = pd.Timestamp(end_date) - pd.Timestamp(start_date)
        days_diff = days_diff.days

        current_date = pd.Timestamp(start_date)
        
        dates = [current_date + datetime.timedelta(diff) for diff in range(days_diff + 1)]
        dates = [d.strftime("%Y-%m-%d") for d in dates]
 
        i = 0
        while i < len(dates):
            try:
                earnings_data += get_earnings_for_date(dates[i])
            except Exception:
                pass
            
            i += 1
            
        return earnings_data


def get_currencies(headers=default_headers):
    # Returns the currencies table from Yahoo Finance
    site = "https://finance.yahoo.com/currencies"
    return pd.read_html(requests.get(site, headers=headers).text)[0]


def get_futures(headers=default_headers):
    # Returns the futures table from Yahoo Finance
    site = "https://finance.yahoo.com/commodities"
    return pd.read_html(requests.get(site, headers=headers).text)[0]


def get_undervalued_large_caps(headers=default_headers):
    # Returns the undervalued large caps table from Yahoo Finance
    site = "https://finance.yahoo.com/screener/predefined/undervalued_large_caps?offset=0&count=100"
    return pd.read_html(requests.get(site, headers=headers).text)[0]


