import requests
import re
import ftplib
import io
import random
import warnings
import os
import datetime
import pandas
import yfinance

# HEAVILY MODIFIED FROM YAHOO-FIN LIBRARY AT: https://pypi.org/project/yahoo-fin/#history
# This file contains TNS, cache based functions and the Ticker class
# TNS links TICKERS, INDEXES and COMPANIES together
# This file should be called when the program starts

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
default_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/120.0.0.0 Safari/537.3'}


def _tickers_sp500_():  # Downloads list of tickers currently listed in the S&P 500
    sp500 = pandas.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    sp_tickers = []
    for i in range(len(sp500)):
        sp_tickers.append(f"{sp500.values[i][0]}§{sp500.values[i][1]}§{sp500.values[i][2]}§"
                          f" {sp500.values[i][3]}§{sp500.values[i][4]}§{sp500.values[i][6]}")

    return sp_tickers


def _nasdaq_trader_(search_param):  # Downloads list of nasdaq tickers
    ftp = ftplib.FTP("ftp.nasdaqtrader.com")
    ftp.login()
    ftp.cwd("SymbolDirectory")

    r = io.BytesIO()
    ftp.retrbinary(f'RETR {search_param}.txt', r.write)

    info = r.getvalue().decode()
    splits = info.split("|")

    tickers = [x for x in splits if len(x) > 1]
    ticker_data = []
    for i in range(len(tickers) - 4):
        if tickers[i] == "100" and "-" in tickers[i + 2]:
            stock_ticker = tickers[i + 1].split('\r\n')[1]
            stock_name = tickers[i + 2].split(" - ")[0]
            stock_type = str(tickers[i + 2].split(" - ")[1:])[2:-2]
            ticker_data.append(f"{stock_ticker}§{stock_name}§{stock_type}")
        elif tickers[i] == "100" and "-" not in tickers[i + 2] and "test stock" not in tickers[i + 2].lower():
            stock_ticker = tickers[i + 1].split('\r\n')[1]
            ticker_data.append(f"{stock_ticker}§{tickers[i + 2]}")

    return ticker_data


def _tickers_nasdaq_():  # Nasdaq stocks
    return _nasdaq_trader_("nasdaqlisted")


def _tickers_us_other_():  # Nasdaq other, funds, etfs, etc.
    return _nasdaq_trader_("otherlisted")


def _tickers_dow_():  # Dow_Jones_Industrial_Average
    site = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
    table = pandas.read_html(site, attrs={"id": "constituents"})[0]
    dow_tickers = []
    for i in range(len(table)):
        dow_tickers.append(f"{table.values[i][2]}§{table.values[i][0]}§{table.values[i][6]}§{table.values[i][1]}§"
                           f"{table.values[i][3]}")

    return dow_tickers


def _tickers_nifty50_():  # NIFTY 50, India
    site = "https://en.wikipedia.org/wiki/NIFTY_50"
    table = pandas.read_html(site, attrs={"id": "constituents"})[0]
    _nifty50 = []
    for i in range(len(table)):
        _nifty50.append(f"{table.values[i][1]}§{table.values[i][0]}§{table.values[i][2]}")

    return _nifty50


def _tickers_ftse100_():  # UK 100
    table = pandas.read_html("https://en.wikipedia.org/wiki/FTSE_100_Index", attrs={"id": "constituents"})[0]
    _ftse100 = []
    for i in range(len(table)):
        if str(table.values[i][1]).endswith("."):
            _ftse100.append(f"{table.values[i][1]}L§{table.values[i][0]}§{table.values[i][2]}")
        else:
            _ftse100.append(f"{table.values[i][1]}.L§{table.values[i][0]}§{table.values[i][2]}")
    return _ftse100


def _tickers_ftse250_():  # UK 250
    table = pandas.read_html("https://en.wikipedia.org/wiki/FTSE_250_Index", attrs={"id": "constituents"})[0]
    _ftse250 = []
    for i in range(len(table)):
        if str(table.values[i][1]).endswith("."):
            _ftse250.append(f"{table.values[i][1]}L§{table.values[i][0]}§{table.values[i][2]}")
        else:
            _ftse250.append(f"{table.values[i][1]}.L§{table.values[i][0]}§{table.values[i][2]}")
    return _ftse250


def __writer__(file, refresh_days):
    with open(f"TickerData/{file}.txt", "w", encoding="utf-8") as f:
        f.write(f"# reload+after+{datetime.datetime.now() + datetime.timedelta(days=refresh_days)}\n")
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
    if not os.path.exists(f"TickerData/{file}.txt"):
        print(f"Downloading {file} tickers...")
        ticker_info = __writer__(file, refresh_days)
    else:
        with open(f"TickerData/{file}.txt", "r", encoding="utf-8") as f:
            file_time = datetime.datetime.strptime(f.readline().split("+")[2].replace("\n", ""),
                                                   "%Y-%m-%d %H:%M:%S.%f")
            if file_time < datetime.datetime.now():
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
        f.write(f"# reload+after+{datetime.datetime.now() + datetime.timedelta(days=refresh_days)}\n")
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
    if not os.path.exists(f"TickerData/lse.xlsx"):
        print("LSE tickers not found, please download the file from "
              "https://www.londonstockexchange.com/reports?tab=instruments, then save it as lse.xlsx in the "
              "TickerData folder")
        exit()
    else:
        print(f"Downloading lse tickers...")
        data = pandas.read_excel(f"TickerData/lse.xlsx", None)
        all_eq = data['1.0 All Equity'].values.tolist()[8:]
        all_no_eq = data['2.0 All Non-Equity'].values.tolist()[8:]
        __lse_writer__(all_eq, "lse", 31)
        __lse_writer__(all_no_eq, "lse_eq", 31)
        os.rename("TickerData/lse.xlsx", "TickerData/lse_old.xlsx")
        return all_eq, all_no_eq


def _refresh_lse_tickers_():
    if not os.path.exists(f"TickerData/lse.txt") or not os.path.exists(f"TickerData/lse_eq.txt"):
        return __lse_reader__()
    else:
        with open(f"TickerData/lse.txt", "r", encoding="utf-8") as f:
            file_time = datetime.datetime.strptime(f.readline().split("+")[2].replace("\n", ""),
                                                   "%Y-%m-%d %H:%M:%S.%f")
            if file_time < datetime.datetime.now():
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
        t_object = yfinance.Ticker(_ticker)
        t_info = t_object.info
    except requests.exceptions.HTTPError:
        print(f"Ticker {_ticker} profile failed to load: HTTPError")
        return {}
    ticker_profile = {}
    with open(f"TickerData/Tickers/{_ticker}/profile.txt", "w", encoding="utf-8") as f:
        r_day_add, r_hour_add = random.randint(0, 3), random.randint(0, 23)
        f.write(
            f"# reload+after+{datetime.datetime.now() + datetime.timedelta(days=12 + r_day_add) + datetime.timedelta(hours=r_hour_add)}\n")
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
    if os.path.exists(f"TickerData/Tickers/{_ticker}/profile.txt"):
        with open(f"TickerData/Tickers/{_ticker}/profile.txt", "r", encoding="utf-8") as f:
            file_time = datetime.datetime.strptime(f.readline().split("+")[2].replace("\n", ""),
                                                   "%Y-%m-%d %H:%M:%S.%f")
            if file_time < datetime.datetime.now():
                ticker_profile = __ticker_info_writer__(_ticker)
                print(f"Reloaded ticker profile for {_ticker}")
            else:
                ticker_profile = {}
                for line in f.readlines():
                    key, value = line.replace("\n", "").split("§")
                    ticker_profile.update({key: value})
        return ticker_profile
    elif not os.path.exists(f"TickerData/Tickers/{_ticker}"):
        os.mkdir(f"TickerData/Tickers/{_ticker}")
        ticker_profile = __ticker_info_writer__(_ticker)
        return ticker_profile
    else:
        print(f"Skipped folder {_ticker}")
        return None

#########################################################################
# START OF CACHE LOAD SYSTEM - Before this line no file manipulation


if not os.path.exists("TickerData"):
    os.mkdir("TickerData")
    print("Created TickerData directory...")
else:
    print("Found TickerData directory...")

if not os.path.exists("TickerData/Tickers"):
    os.mkdir("TickerData/Tickers")


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
tickers_other = {'nasdaq_other': nasdaq_other, 'lse_eq': lse_eq}
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


def tns(names, other=False):  # ticker name system  # todo add ETF/TYPE searching support
    ticker_results = {}
    for name in names:
        related_tickers = _tns_dict_from_search(name, tickers, indexes)

        # if no tickers found in {tickers} or if other=True, search {tickers_other}
        if not related_tickers or other:
            related_tickers = _tns_dict_from_search(name, tickers_other, indexes, related_tickers)

        # remove empty values from related_tickers
        for key in related_tickers.keys():
            for value in related_tickers[key]:
                if value == "":
                    related_tickers[key].remove(value)
        ticker_results.update({name: related_tickers})
    return ticker_results


def load_profiles():
    exec_dict = {}
    comp_names_l = {}
    comp_names_s = {}
    for key in tickers_all.keys():
        counter = 0
        for ticker in tickers_all[key]:
            counter += 1
            ticker_profile = load_ticker_info(ticker[0])
            if ticker_profile:
                if counter % 1000 == 0:
                    print(f"{counter}/{len(tickers_all[key])} - {ticker[0]}")
                if "companyOfficers" in ticker_profile:
                    exec_dict.update({ticker[0]: eval(ticker_profile["companyOfficers"])})
                if "longName" in ticker_profile:
                    comp_names_l.update({ticker[0]: ticker_profile["longName"]})
                if "shortName" in ticker_profile:
                    comp_names_s.update({ticker[0]: ticker_profile["shortName"]})

    return exec_dict, comp_names_l, comp_names_s


# class of wrappers to return data from profile data
class _Data:
    def __init__(self):
        print("Loading profile data...")
        self.exec_dict, self.comp_names_l, self.comp_names_s = load_profiles()
        print("Loaded profile data successfully...\nFinished loading...\n"
              "-------------------------------------------")


data = _Data()

