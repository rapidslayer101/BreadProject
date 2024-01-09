import requests as _req
import re
from ftplib import FTP as _FTP
from io import BytesIO as _BytesIO
from random import randint as _randint
from json import loads as _json_loads
from warnings import simplefilter as _warning_filter_
from os import rename as _rename, mkdir as _mkdir, listdir as _listdir
from os.path import exists as _exists
from datetime import datetime, timedelta
from pandas import read_excel, read_html, Timestamp
from requests_html import HTMLSession as _HTMLSession
from yfinance import Ticker as YF_ticker


# HEAVILY MODIFIED FROM YAHOO-FIN LIBRARY AT: https://pypi.org/project/yahoo-fin/#history
# This file contains TNS, cache based functions and the Ticker class
# TNS links TICKERS, INDEXES and COMPANIES together
# This file should be called when the program starts


if not _exists("TickerData"):
    _mkdir("TickerData")
    print("Created TickerData directory...")
else:
    print("Found TickerData directory...")

if not _exists("TickerData/Tickers"):
    _mkdir("TickerData/Tickers")

_warning_filter_(action='ignore', category=FutureWarning)
_warning_filter_(action='ignore', category=UserWarning)
default_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/120.0.0.0 Safari/537.3'}


def _tickers_sp500_():  # Downloads list of tickers currently listed in the S&P 500
    sp500 = read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    sp_tickers = []
    for i in range(len(sp500)):
        sp_tickers.append(f"{sp500.values[i][0]}§{sp500.values[i][1]}§{sp500.values[i][2]}§"
                          f" {sp500.values[i][3]}§{sp500.values[i][4]}§{sp500.values[i][6]}")

    return sp_tickers


def _nasdaq_trader_(search_param):  # Downloads list of nasdaq tickers
    ftp = _FTP("ftp.nasdaqtrader.com")
    ftp.login()
    ftp.cwd("SymbolDirectory")

    r = _BytesIO()
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


def _tickers_nasdaq_():  # Nasdaq stocks
    return _nasdaq_trader_("nasdaqlisted")


def _tickers_us_other_():  # Nasdaq other, funds, etfs, etc.
    return _nasdaq_trader_("otherlisted")
    

def _tickers_dow_():  # Dow_Jones_Industrial_Average
    site = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
    table = read_html(site, attrs={"id": "constituents"})[0]
    dow_tickers = []
    for i in range(len(table)):
        dow_tickers.append(f"{table.values[i][2]}§{table.values[i][0]}§{table.values[i][6]}§{table.values[i][1]}§"
                           f"{table.values[i][3]}")

    return dow_tickers    


def _tickers_nifty50_():  # NIFTY 50, India
    site = "https://en.wikipedia.org/wiki/NIFTY_50"
    table = read_html(site, attrs={"id": "constituents"})[0]
    nifty50 = []
    for i in range(len(table)):
        nifty50.append(f"{table.values[i][1]}§{table.values[i][0]}§{table.values[i][2]}")

    return nifty50


def _tickers_ftse100_():  # UK 100
    table = read_html("https://en.wikipedia.org/wiki/FTSE_100_Index", attrs={"id": "constituents"})[0]
    ftse100 = []
    for i in range(len(table)):
        if str(table.values[i][1]).endswith("."):
            ftse100.append(f"{table.values[i][1]}L§{table.values[i][0]}§{table.values[i][2]}")
        else:
            ftse100.append(f"{table.values[i][1]}.L§{table.values[i][0]}§{table.values[i][2]}")
    return ftse100
    

def _tickers_ftse250_():  # UK 250
    table = read_html("https://en.wikipedia.org/wiki/FTSE_250_Index", attrs={"id": "constituents"})[0]
    ftse250 = []
    for i in range(len(table)):
        if str(table.values[i][1]).endswith("."):
            ftse250.append(f"{table.values[i][1]}L§{table.values[i][0]}§{table.values[i][2]}")
        else:
            ftse250.append(f"{table.values[i][1]}.L§{table.values[i][0]}§{table.values[i][2]}")
    return ftse250


def __writer__(file, refresh_days):
    with open(f"TickerData/{file}.txt", "w", encoding="utf-8") as f:
        f.write(f"# reload+after+{datetime.now()+timedelta(days=refresh_days)}\n")
        if file == "sp_500":
            data = _tickers_sp500_()
        elif file == "nasdaq":
            data = _tickers_nasdaq_()
        elif file == "nasdaq_other":
            data = _tickers_us_other_()
        elif file == "dow_jones":
            data = _tickers_dow_()
        elif file == "nifty50":
            data = _tickers_nifty50_()
        elif file == "ftse100":
            data = _tickers_ftse100_()
        elif file == "ftse250":
            data = _tickers_ftse250_()

        ticker_info = []
        for ticker in data:
            f.write(f"{ticker}\n")
            ticker_info.append(ticker.split("§"))

    return ticker_info


def _refresh_ticker_data_(file, refresh_days):
    if not exists(f"TickerData/{file}.txt"):
        print(f"Downloading {file} tickers...")
        ticker_info = __writer__(file, refresh_days)
    else:
        with open(f"TickerData/{file}.txt", "r", encoding="utf-8") as f:
            file_time = datetime.strptime(f.readline().split("+")[2].replace("\n", ""), "%Y-%m-%d %H:%M:%S.%f")
            if file_time < datetime.now():
                ticker_info = __writer__(file, refresh_days)
                print(f"Found and refreshed {file} tickers...")
            else:
                print(f"Found {file} tickers...")
                ticker_info = []
                for ticker in f.readlines():
                    ticker_info.append(ticker.replace("\n", "").split("§"))
    return ticker_info


def __lse_writer__(data, file, refresh_days):
    with open(f"TickerData/{file}.txt", "w", encoding="utf-8") as f:
        f.write(f"# reload+after+{datetime.now()+timedelta(days=refresh_days)}\n")
        for ticker in data:
            line = ""
            for i in range(len(ticker)):
                if i == 0:
                    if ticker[i].endswith("."):
                        line += f"{ticker[i]}L§"
                    else:
                        line += f"{ticker[i]}.L§"
                else:
                    line += f"{ticker[i]}§"
            f.write(f"{line[:-1]}\n")


def __lse_reader__():
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
        __lse_writer__(all_eq, "lse", 31)
        __lse_writer__(all_no_eq, "lse_eq", 31)
        _rename("TickerData/lse.xlsx", "TickerData/lse_old.xlsx")
        return all_eq, all_no_eq


def _refresh_lse_tickers_():
    if not exists(f"TickerData/lse.txt") or not exists(f"TickerData/lse_eq.txt"):
        return __lse_reader__()
    else:
        with open(f"TickerData/lse.txt", "r", encoding="utf-8") as f:
            file_time = datetime.strptime(f.readline().split("+")[2].replace("\n", ""), "%Y-%m-%d %H:%M:%S.%f")
            if file_time < datetime.now():
                return __lse_reader__()
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


def __ticker_info_writer__(_ticker):
    try:
        t_object = Ticker(_ticker)
        t_info = t_object.info
    except _req.exceptions.HTTPError:
        print(f"Ticker {_ticker} profile failed to load: HTTPError")
        return {}
    ticker_profile = {}
    with open(f"TickerData/Tickers/{_ticker}/profile.txt", "w", encoding="utf-8") as f:
        r_day_add, r_hour_add = _randint(0, 3), _randint(0, 23)
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


def _site_scraper_(site):
    # load website so all contents can be scraped
    tables = read_html(_req.get(site, headers=default_headers).text)
    data = {}
    for table in tables:
        for value in table.values:
            data.update({value[0]: str(value[1:])[2:-2]})

    return data


def get_ticker_data(ticker):
    # Scrapes data elements found on Yahoo Finance's quote page
    site = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}"
    return _site_scraper_(site)


def get_ticker_stats(ticker):
    # Scrapes information from the statistics page on Yahoo Finance
    stats_site = f"https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}"
    return _site_scraper_(stats_site)


# loads company profile from cache or downloads it, returns profile data
def load_ticker_info(_ticker):
    if exists(f"TickerData/Tickers/{_ticker}/profile.txt"):
        with open(f"TickerData/Tickers/{_ticker}/profile.txt", "r", encoding="utf-8") as f:
            file_time = datetime.strptime(f.readline().split("+")[2].replace("\n", ""), "%Y-%m-%d %H:%M:%S.%f")
            if file_time < datetime.now():
                ticker_profile = __ticker_info_writer__(_ticker)
                print(f"Reloaded ticker profile for {_ticker}")
            else:
                ticker_profile = {}
                for line in f.readlines():
                    key, value = line.replace("\n", "").split("§")
                    ticker_profile.update({key: value})
    else:
        if not exists(f"TickerData/Tickers/{_ticker}"):
            _mkdir(f"TickerData/Tickers/{_ticker}")
        ticker_profile = __ticker_info_writer__(_ticker)
    return ticker_profile


# todo this function does the same as t_object.institutional_holders,
#  t_object.major_holders, t_object.mutualfund_holders
def get_holders(ticker):
    # Scrapes the Holders page from Yahoo Finance for an input ticker
    holders_site = f"https://finance.yahoo.com/quote/{ticker}/holders?p={ticker}"
    tables = read_html(_req.get(holders_site, headers=default_headers).text)
    table_names = ["Major Holders", "Direct Holders (Forms 3 and 4)",
                   "Top Institutional Holders", "Top Mutual Fund Holders"]
    table_mapper = {key: val for key, val in zip(table_names, tables)}

    return table_mapper       


# todo provides 5 tables of unique data, check usefulness
def get_analysts_info(ticker):
    # Scrapes the Analysts page from Yahoo Finance for an input ticker
    analysts_site = f"https://finance.yahoo.com/quote/{ticker}/analysts?p={ticker}"
    tables = read_html(_req.get(analysts_site, headers=default_headers).text)
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


def __raw_get_daily_info__(site):
    session = _HTMLSession()
    resp = session.get(site)
    tables = read_html(resp.html.raw_html)
    df = tables[0].copy()
    df.columns = tables[0].columns
    del df["52 Week Range"]
    df["% Change"] = df["% Change"].map(lambda x: float(x.strip("%+").replace(",", "")))
    fields_to_change = [x for x in df.columns.tolist() if "Vol" in x or x == "Market Cap"]
    
    for field in fields_to_change:
        if type(df[field][0]) == str:
            df[field] = df[field].map(_convert_to_numeric_)
            
    session.close()
    
    return df
    

def get_day_most_active(offset: int = 0, count: int = 100):  # todo NOT POSSIBLE TO SCRAPE REGIONS OTHER THAN US
    return __raw_get_daily_info__(f"https://finance.yahoo.com/most-active?offset={offset}&count={count}")


def get_day_gainers(count: int = 100):  # todo NOT POSSIBLE TO SCRAPE REGIONS OTHER THAN US
    return __raw_get_daily_info__(f"https://finance.yahoo.com/gainers?offset=0&count={count}")


def get_day_losers(count: int = 100):  # todo NOT POSSIBLE TO SCRAPE REGIONS OTHER THAN US
    return __raw_get_daily_info__(f"https://finance.yahoo.com/losers?offset=0&count={count}")


def get_day_trending_tickers():
    return __raw_get_daily_info__(f"https://finance.yahoo.com/trending-tickers")


def get_day_top_etfs(count: int = 100):  # todo NOT POSSIBLE TO SCRAPE REGIONS OTHER THAN US
    return __raw_get_daily_info__(f"https://finance.yahoo.com/etfs?offset=0&count={count}")


def get_day_top_mutual(count: int = 100):  # todo NOT POSSIBLE TO SCRAPE REGIONS OTHER THAN US
    return __raw_get_daily_info__(f"https://finance.yahoo.com/mutualfunds?offset=0&count={count}")


def get_day_top_futures():
    # why is there an unnamed column???
    return read_html(_req.get("https://finance.yahoo.com/commodities", headers=default_headers).text)[0]


def get_day_highest_open_interest(count: int = 100):
    # uses a different table format than other daily infos
    return read_html(_req.get(f"https://finance.yahoo.com/options/highest-open-interest?"
                             f"offset=0&count={count}", headers=default_headers).text)[0]


def get_day_highest_implied_volatility(count: int = 100):
    # uses a different table format than other daily infos
    return read_html(_req.get(f"https://finance.yahoo.com/options/highest-implied-volatility?"
                             f"offset=0&count={count}", headers=default_headers).text)[0]


def get_day_top_world_indices():
    return __raw_get_daily_info__(f"https://finance.yahoo.com/world-indices")


def get_day_top_forex_rates():
    return __raw_get_daily_info__(f"https://finance.yahoo.com/currencies")


def get_day_top_us_bonds():
    return __raw_get_daily_info__(f"https://finance.yahoo.com/bonds")


def get_day_top_crypto(offset: int = 0, count: int = 100):
    # Gets the top 100 Cryptocurrencies by Market Cap
    session = _HTMLSession()
    resp = session.get(f"https://finance.yahoo.com/cryptocurrencies?offset={offset}&count={count}")
    df = read_html(resp.html.raw_html)[0].copy()
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


### Earnings functions
def _parse_earnings_json(url):
        resp = _req.get(url, headers=default_headers)
        
        content = resp.content.decode(encoding='utf-8', errors='strict')
        
        page_data = [row for row in content.split(
            '\n') if row.startswith('root.App.main = ')][0][:-1]
        
        page_data = page_data.split('root.App.main = ', 1)[1]
        
        return _json_loads(page_data)


def get_earnings_history(ticker):
    # Returns the earnings calendar history of the input ticker with EPS actual vs. expected data.'''
    url = f"https://finance.yahoo.com/calendar/earnings?symbol={ticker}"
    return read_html(_req.get(url, headers=default_headers).text)[0]


# todo does not scrap LSE, check against yf.Ticker(ticker).get_earnings()
def get_earnings_for_date(date, offset=0, count=100):
    # TODO LIMITATION ONLY SHOWS REGION US
    # Returns a dictionary of stock tickers with earnings expected on the input date.
    # The dictionary contains the expected EPS values for each stock if available.
    date = Timestamp(date).strftime("%Y-%m-%d")
    url = f"https://finance.yahoo.com/calendar/earnings?day={date}&offset={offset}&size={count}"
    # https://query2.finance.yahoo.com/v1/finance/trending/US?count=50&useQuotes=true&fields=logoUrl%2CregularMarketChangePercent

    return read_html(_req.get(url, headers=default_headers).text)[0]


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
    return read_html(_req.get(site, headers=default_headers).text)[0]


def get_futures():
    # Returns the futures table from Yahoo Finance
    site = "https://finance.yahoo.com/commodities"
    return read_html(_req.get(site, headers=default_headers).text)[0]


def get_undervalued_large_caps(offset: int = 0, count: int = 100):  # todo NOT POSSIBLE TO SCRAPE REGIONS OTHER THAN US
    # Returns the undervalued large caps table from Yahoo Finance
    site = "https://finance.yahoo.com/screener/predefined/undervalued_large_caps?offset={offset}&count={count}"
    return read_html(_req.get(site, headers=default_headers).text)[0]


#########################################################################
# START OF CACHE LOAD SYSTEM


# type ticker: [ticker, company/type (e.g. bond, etf), other data]
# type index: [ticker, company, other data]
# type weighted index: [ticker, company, weight, other data]

sp_500 = _refresh_ticker_data_("sp_500", 7)  # type index
nasdaq = _refresh_ticker_data_("nasdaq", 7)  # type tickers
nasdaq_other = _refresh_ticker_data_("nasdaq_other", 7)  # type tickers
dow_jones = _refresh_ticker_data_("dow_jones", 7)  # type weighted index
nifty50 = _refresh_ticker_data_("nifty50", 7)  # type index
ftse100 = _refresh_ticker_data_("ftse100", 7)  # type index
ftse250 = _refresh_ticker_data_("ftse250", 7)  # type index
lse, lse_eq = _refresh_lse_tickers_()  # type tickers

tickers = {'nasdaq': nasdaq, 'lse': lse}
tickers_all = {'nasdaq': nasdaq, 'nasdaq_other': nasdaq_other, 'lse': lse, 'lse_eq': lse_eq}
indexes = {'sp_500': sp_500, 'dow_jones': dow_jones, 'nifty50': nifty50, 'ftse100': ftse100, 'ftse250': ftse250}

print("Loaded tickers and indexes successfully...\n-------------------------------------------")


def _tns_dict_from_search(search, ticker_list, index_list, search_dict=None):
    if not search_dict:
        search_dict = {}
    for key in ticker_list.keys():
        for ticker in ticker_list[key]:
            if re.search(r"\b"+re.escape(search.lower())+r"\b", ticker[1].lower()):
                relevant_indexes = []
                for index in index_list.keys():
                    for _ticker in index_list[index]:
                        if ticker[0] == _ticker[0]:
                            relevant_indexes.append(index)
                search_dict.update({ticker[0]: ticker[1:]+[[relevant_indexes]]})
    return search_dict


def tns(name, other=False):  # ticker name system  # todo add ETF/TYPE searching support
    related_tickers = _tns_dict_from_search(name, tickers, indexes)

    # if no tickers found in {tickers} or if other=True, search {tickers_all}
    if not related_tickers or other:
        related_tickers = _tns_dict_from_search(name, tickers_all, indexes, related_tickers)

    # remove empty values from related_tickers
    for key in related_tickers.keys():
        for value in related_tickers[key]:
            if value == "":
                related_tickers[key].remove(value)

    return related_tickers


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

# code to generate ticker profile cache
#counter = 0
#for ticker_name in lse:
#    counter += 1
#    print(ticker_name[0], load_ticker_info(ticker_name[0]))
#    print(f"{counter}/{len(nasdaq_other)}")
#input()

print("Loading profile data...")
exec_dict = {}
comp_names_l = {}
comp_names_s = {}
for folder in _listdir("TickerData/Tickers"):
    if exists(f"TickerData/Tickers/{folder}/profile.txt"):
        ticker_profile = load_ticker_info(folder)
        if "companyOfficers" in ticker_profile:
            exec_dict.update({folder: eval(ticker_profile["companyOfficers"])})
        if "longName" in ticker_profile:
            comp_names_l.update({folder: ticker_profile["longName"]})
        if "shortName" in ticker_profile:
            comp_names_s.update({folder: ticker_profile["shortName"]})


def get_exec_data():
    return exec_dict


def get_comp_names_l():
    return comp_names_l


def get_comp_names_s():
    return comp_names_s


print("Loaded profile data successfully...\nFinished loading ticker_loader.py...\n"
      "-------------------------------------------")


class TNS:
    def __init__(self, name, other=False):
        self.name = name
        self.tickers = tns(name, other=other)
        if not self.tickers:
            print("Ticker not found: TNS failed to resolve ticker")
        else:
            print(self.tickers)

    def get_objects(self):
        return [Ticker(key) for key in self.tickers.keys()]


class Ticker:
    def __init__(self, ticker):
        self.ticker_obj = YF_ticker(ticker)
        self.profile = None

    def get_profile(self):
        if self.profile:
            return self.profile
        else:
            self.profile = load_ticker_info(self.ticker_obj.ticker)
            return self.profile

    def get_news(self):
        return self.ticker_obj.news
