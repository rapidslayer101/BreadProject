import requests as req
from ftplib import FTP
from io import BytesIO
from random import randint
from json import loads as json_loads
from warnings import simplefilter as warning_filter
from os import rename, mkdir
from os.path import exists
from datetime import datetime, timedelta
from pandas import read_excel, read_html, Timestamp
from yfinance import Ticker


# file of functions to pull tickers and indexes from various sources
# MODIFIED FROM YAHOO-FIN LIBRARY AT: https://pypi.org/project/yahoo-fin/#history

if not exists("TickerData"):
    mkdir("TickerData")
    print("Created TickerData directory...")
else:
    print("Found TickerData directory...")

if not exists("TickerData/Tickers"):
    mkdir("TickerData/Tickers")

warning_filter(action='ignore', category=FutureWarning)
warning_filter(action='ignore', category=UserWarning)
default_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/120.0.0.0 Safari/537.3'}


try:
    from requests_html import HTMLSession
except Exception:
    print("""Warning - Certain functionality 
             requires requests_html, which is not installed.
             
             Install using: pip install requests_html""")

    
base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"


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
    sp500 = read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    sp_tickers = []
    for i in range(len(sp500)):
        sp_tickers.append(f"{sp500.values[i][0]}§{sp500.values[i][1]}§{sp500.values[i][2]}§"
                          f" {sp500.values[i][3]}§{sp500.values[i][4]}§{sp500.values[i][6]}")

    return sp_tickers


def _nasdaq_trader(search_param):  # Downloads list of nasdaq tickers
    ftp = FTP("ftp.nasdaqtrader.com")
    ftp.login()
    ftp.cwd("SymbolDirectory")

    r = BytesIO()
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
    table = read_html(site, attrs={"id": "constituents"})[0]
    dow_tickers = []
    for i in range(len(table)):
        dow_tickers.append(f"{table.values[i][2]}§{table.values[i][0]}§{table.values[i][6]}§{table.values[i][1]}§"
                           f"{table.values[i][3]}")

    return dow_tickers    


def tickers_nifty50():  # NIFTY 50, India
    site = "https://en.wikipedia.org/wiki/NIFTY_50"
    table = read_html(site, attrs={"id": "constituents"})[0]
    nifty50 = []
    for i in range(len(table)):
        nifty50.append(f"{table.values[i][1]}§{table.values[i][0]}§{table.values[i][2]}")

    return nifty50


def tickers_ftse100():  # UK 100
    table = read_html("https://en.wikipedia.org/wiki/FTSE_100_Index", attrs={"id": "constituents"})[0]
    ftse100 = []
    for i in range(len(table)):
        ftse100.append(f"{table.values[i][1]}.L§{table.values[i][0]}§{table.values[i][2]}")

    return ftse100
    

def tickers_ftse250():  # UK 250
    table = read_html("https://en.wikipedia.org/wiki/FTSE_250_Index", attrs={"id": "constituents"})[0]
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
    tables = read_html(req.get(site, headers=default_headers).text)
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
    # Scrapes information from the statistics page on Yahoo Finance
    stats_site = f"https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}"
    return _site_scraper(stats_site)


def _ticker_info_writer_(_ticker):
    try:
        t_object = Ticker(_ticker)
        t_info = t_object.info
    except req.exceptions.HTTPError:
        print(f"Ticker {_ticker} profile failed to load: HTTPError")
        return {}
    ticker_profile = {}
    with open(f"TickerData/Tickers/{_ticker}/profile.txt", "w", encoding="utf-8") as f:
        r_day_add, r_hour_add = randint(0, 3), randint(0, 23)
        f.write(f"# reload+after+{datetime.now()+timedelta(days=12+r_day_add)+timedelta(hours=r_hour_add)}\n")
        # the below keys are perceived as mostly live data (gained from get_ticker_data()), so excluded from the cache
        ex_keys = ["previousClose", "open", "dayLow", "dayHigh", "regularMarketPreviousClose", "regularMarketOpen",
                   "regularMarketDayLow", "regularMarketDayHigh", "trailingPE", "forwardPE", "volume",
                   "regularMarketVolume", "averageVolume", "averageVolume10days", "averageDailyVolume10Day", "bid",
                   "ask", "bidSize", "askSize", "marketCap", "fiftyTwoWeekLow", "fiftyTwoWeekHigh", "fiftyDayAverage",
                   "twoHundredDayAverage", "trailingAnnualDividendRate", "trailingAnnualDividendYield",
                   "enterpriseValue", "profitMargins", "floatShares", "sharesOutstanding", "sharesShort",
                   "sharesShortPriorMonth", "sharesShortPreviousMonthDate", "sharesPercentSharesOut",
                   "heldPercentInsiders", "heldPercentInstitutions", "shortRatio", "shortPercentOfFloat",
                   "impliedSharesOutstanding", "bookValue", "priceToBook", "lastFiscalYearEnd", "nextFiscalYearEnd",
                   "mostRecentQuarter", "earningsQuarterlyGrowth", "netIncomeToCommon", "trailingEps",
                   "lastSplitFactor", "lastSplitDate", "enterpriseToRevenue", "enterpriseToEbitda", "52WeekChange",
                   "SandP52WeekChange", "symbol", "underlyingSymbol", "currentPrice", "totalCash", "totalCashPerShare",
                   "ebitda", "totalDebt", "currentRatio", "totalRevenue", "debtToEquity", "revenuePerShare",
                   "returnOnAssets", "returnOnEquity", "grossProfits", "freeCashflow", "operatingCashflow",
                   "revenueGrowth", "operatingMargins", "financialCurrency"]

        for _key in t_info.keys():
            if _key not in ex_keys:
                t_info[_key] = str(t_info[_key]).replace("\n", "")
                f.write(f"{_key}§{t_info[_key]}\n")
                ticker_profile.update({_key: t_info[_key]})
    return ticker_profile


# loads company profile from cache or downloads it, returns profile data
def load_ticker_info(_ticker):
    if exists(f"TickerData/Tickers/{_ticker}/profile.txt"):
        with open(f"TickerData/Tickers/{_ticker}/profile.txt", "r", encoding="utf-8") as f:
            file_time = datetime.strptime(f.readline().split("+")[2].replace("\n", ""), "%Y-%m-%d %H:%M:%S.%f")
            if file_time < datetime.now():
                ticker_profile = _ticker_info_writer_(_ticker)
                print(f"Reloaded ticker profile for {_ticker}")
            else:
                ticker_profile = {}
                for line in f.readlines():
                    key, value = line.replace("\n", "").split("§")
                    ticker_profile.update({key: value})
    else:
        if not exists(f"TickerData/Tickers/{_ticker}"):
            mkdir(f"TickerData/Tickers/{_ticker}")
        ticker_profile = _ticker_info_writer_(_ticker)
    return ticker_profile


# todo this function does the same as t_object.institutional_holders,
#  t_object.major_holders, t_object.mutualfund_holders
def get_holders(ticker):
    # Scrapes the Holders page from Yahoo Finance for an input ticker
    holders_site = f"https://finance.yahoo.com/quote/{ticker}/holders?p={ticker}"
    tables = read_html(req.get(holders_site, headers=default_headers).text)
    table_names = ["Major Holders", "Direct Holders (Forms 3 and 4)",
                   "Top Institutional Holders", "Top Mutual Fund Holders"]
    table_mapper = {key: val for key, val in zip(table_names, tables)}

    return table_mapper       


# todo provides 5 tables of unique data, check usefulness
def get_analysts_info(ticker):
    # Scrapes the Analysts page from Yahoo Finance for an input ticker
    analysts_site = f"https://finance.yahoo.com/quote/{ticker}/analysts?p={ticker}"
    tables = read_html(req.get(analysts_site, headers=default_headers).text)
    table_names = [table.columns[0] for table in tables]
    table_mapper = {key: val for key, val in zip(table_names, tables)}

    return table_mapper


def _raw_get_daily_info(site):
    session = HTMLSession()
    resp = session.get(site)
    tables = read_html(resp.html.raw_html)
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
    

def get_day_most_active(offset: int = 0, count: int = 100):  # todo NOT POSSIBLE TO SCRAPE REGIONS OTHER THAN US
    return _raw_get_daily_info(f"https://finance.yahoo.com/most-active?offset={offset}&count={count}")


def get_day_gainers(count: int = 100):  # todo NOT POSSIBLE TO SCRAPE REGIONS OTHER THAN US
    return _raw_get_daily_info(f"https://finance.yahoo.com/gainers?offset=0&count={count}")


def get_day_losers(count: int = 100):  # todo NOT POSSIBLE TO SCRAPE REGIONS OTHER THAN US
    return _raw_get_daily_info(f"https://finance.yahoo.com/losers?offset=0&count={count}")


def get_day_trending_tickers():
    return _raw_get_daily_info(f"https://finance.yahoo.com/trending-tickers")


def get_day_top_etfs(count: int = 100):  # todo NOT POSSIBLE TO SCRAPE REGIONS OTHER THAN US
    return _raw_get_daily_info(f"https://finance.yahoo.com/etfs?offset=0&count={count}")


def get_day_top_mutual(count: int = 100):  # todo NOT POSSIBLE TO SCRAPE REGIONS OTHER THAN US
    return _raw_get_daily_info(f"https://finance.yahoo.com/mutualfunds?offset=0&count={count}")


def get_day_top_futures():
    # why is there a unnamed column???
    return read_html(req.get("https://finance.yahoo.com/commodities", headers=default_headers).text)[0]


def get_day_highest_open_interest(count: int = 100):
    # uses a different table format than other daily infos
    return read_html(req.get(f"https://finance.yahoo.com/options/highest-open-interest?"
                                     f"offset=0&count={count}", headers=default_headers).text)[0]


def get_day_highest_implied_volatility(count: int = 100):
    # uses a different table format than other daily infos
    return read_html(req.get(f"https://finance.yahoo.com/options/highest-implied-volatility?"
                                     f"offset=0&count={count}", headers=default_headers).text)[0]


def get_day_top_world_indices():
    return _raw_get_daily_info(f"https://finance.yahoo.com/world-indices")


def get_day_top_forex_rates():
    return _raw_get_daily_info(f"https://finance.yahoo.com/currencies")


def get_day_top_us_bonds():
    return _raw_get_daily_info(f"https://finance.yahoo.com/bonds")


def get_day_top_crypto(offset: int = 0, count: int = 100):
    # Gets the top 100 Cryptocurrencies by Market Cap
    session = HTMLSession()
    resp = session.get(f"https://finance.yahoo.com/cryptocurrencies?offset={offset}&count={count}")
    df = read_html(resp.html.raw_html)[0].copy()
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
def _parse_earnings_json(url):
        resp = req.get(url, headers=default_headers)
        
        content = resp.content.decode(encoding='utf-8', errors='strict')
        
        page_data = [row for row in content.split(
            '\n') if row.startswith('root.App.main = ')][0][:-1]
        
        page_data = page_data.split('root.App.main = ', 1)[1]
        
        return json_loads(page_data)


def get_earnings_history(ticker):
    # Returns the earnings calendar history of the input ticker with EPS actual vs. expected data.'''
    url = f"https://finance.yahoo.com/calendar/earnings?symbol={ticker}"
    return read_html(req.get(url, headers=default_headers).text)[0]


# todo does not scrap LSE, check against yf.Ticker(ticker).get_earnings()
def get_earnings_for_date(date, offset=0, count=100):
    # TODO LIMITATION ONLY SHOWS REGION US
    # Returns a dictionary of stock tickers with earnings expected on the input date.
    # The dictionary contains the expected EPS values for each stock if available.
    date = Timestamp(date).strftime("%Y-%m-%d")
    url = f"https://finance.yahoo.com/calendar/earnings?day={date}&offset={offset}&size={count}"
    # https://query2.finance.yahoo.com/v1/finance/trending/US?count=50&useQuotes=true&fields=logoUrl%2CregularMarketChangePercent

    return read_html(req.get(url, headers=default_headers).text)[0]


def get_earnings_in_date_range(start_date, end_date):

        '''Inputs: @start_date
                   @end_date
                   
           Returns the stock tickers with expected EPS data for all dates in the
           input range (inclusive of the start_date and end_date.'''
    
        earnings_data = []

        days_diff = Timestamp(end_date) - Timestamp(start_date)
        days_diff = days_diff.days

        current_date = Timestamp(start_date)
        
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


def get_currencies():
    # Returns the currencies table from Yahoo Finance
    site = "https://finance.yahoo.com/currencies"
    return read_html(req.get(site, headers=default_headers).text)[0]


def get_futures():
    # Returns the futures table from Yahoo Finance
    site = "https://finance.yahoo.com/commodities"
    return read_html(req.get(site, headers=default_headers).text)[0]


def get_undervalued_large_caps(offset: int = 0, count: int = 100):  # todo NOT POSSIBLE TO SCRAPE REGIONS OTHER THAN US
    # Returns the undervalued large caps table from Yahoo Finance
    site = "https://finance.yahoo.com/screener/predefined/undervalued_large_caps?offset={offset}&count={count}"
    return read_html(req.get(site, headers=default_headers).text)[0]


