from tickers_and_indexes import *
from random import randint
from datetime import datetime, timedelta
from os import listdir
import yfinance as yf

# This file contains the TNS and other cache based functions
# TNS links TICKERS, INDEXES and COMPANIES together
# This file should be called when the program starts


# type ticker: [ticker, company/type (e.g. bond, etf), other data]
# type index: [ticker, company, other data]
# type weighted index: [ticker, company, weight, other data]


sp_500 = refresh_ticker_data("sp_500", 7)  # type index
nasdaq = refresh_ticker_data("nasdaq", 7)  # type tickers
nasdaq_other = refresh_ticker_data("nasdaq_other", 7)  # type tickers
dow_jones = refresh_ticker_data("dow_jones", 7)  # type weighted index
nifty50 = refresh_ticker_data("nifty50", 7)  # type index
ftse100 = refresh_ticker_data("ftse100", 7)  # type index
ftse250 = refresh_ticker_data("ftse250", 7)  # type index
lse, lse_eq = refresh_lse_tickers()  # type tickers

tickers = {'nasdaq': nasdaq, 'nasdaq_other': nasdaq_other, 'lse': lse, 'lse_eq': lse_eq}
indexes = {'sp_500': sp_500, 'dow_jones': dow_jones, 'nifty50': nifty50, 'ftse100': ftse100, 'ftse250': ftse250}

print("Loaded tickers and indexes successfully...\n-------------------------------------------")


def tns(name):  # ticker name system  # todo work in progress, add ETF searching support 2nd indexed
    related_tickers = []
    for key in tickers.keys():
        for ticker in tickers[key]:
            if re.search(r"\b"+re.escape(name.lower())+r"\b", ticker[1].lower()):
                related_tickers.append([ticker[0], ticker[1]])

    relevant_indexes = []
    for ticker in related_tickers:
        for key in indexes.keys():
            for _ticker in indexes[key]:
                if ticker[0] == _ticker[0]:
                    relevant_indexes.append(key)

    if len(related_tickers) == 0:
        return "ERROR: Ticker not found"
    else:
        return related_tickers, relevant_indexes


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


def _ticker_info_writer_(_ticker):
    try:
        t_object = yf.Ticker(_ticker)
        t_info = t_object.info
    except requests.exceptions.HTTPError:
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


# code to generate ticker profile cache
#counter = 0
#for ticker_name in nasdaq_other:
#    counter += 1
#    print(ticker_name[0], load_ticker_info(ticker_name[0]))
#    print(f"{counter}/{len(nasdaq_other)}")
#input()

print("Loading profile data...")
exec_dict = {}
comp_names_l = {}
comp_names_s = {}
for folder in listdir("TickerData/Tickers"):
    if exists(f"TickerData/Tickers/{folder}/profile.txt"):
        with open(f"TickerData/Tickers/{folder}/profile.txt", "r", encoding="utf-8") as f:
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


if __name__ == "__main__":
    print("File loaded directly, running tests...")
    # lse = ["SHRS", "ETFS", "DPRS", "OTHR"]
    # todo detect type of ticker loaded
    # todo improve TNS for ETF type finder, eg ISF.L working (basically checking 2nd index)
    # nasdaq = ??? a mess of like 400 different types, more research needed

    while True:
        c_name = input("Ticker name: ")
        #c_name = "Tesla"
        c_ticker, c_index = tns(c_name)
        if not c_ticker:
            print("Ticker not found: TNS failed to resolve ticker")
        else:
            break
    #print(c_ticker[0][0], c_index)
    print(c_ticker, c_index)

    ticker_data = tns_check(c_ticker[0][0], c_name)

    print(c_ticker[0][0], c_index)
    print(ticker_data)
    ticker_stats = get_ticker_stats(c_ticker[0][0])
    if "Previous Close" in ticker_stats.keys():
        print("Ticker doesnt have stats")
        ticker_stats = {}
    else:
        print(ticker_stats)

    ticker_data = load_ticker_info(c_ticker[0][0])  # loads from cache or generates cache
    # todo if ticker_data = {} deal with error
    print(ticker_data)
    print("\n")

    #input("Enter to fetch all data: ")
    t_object = yf.Ticker(c_ticker[0][0])

    # todo testing and ordering in alphabetical order
    # Below are all the t_object functions
    #print(t_object.actions)  # returns dividends and stock split dates
    #print(get_analysts_info(c_ticker[0][0]))  # returns 5 tables of data
    #print(t_object.balance_sheet)  # returns table 81 rows, 4 columns
    #print(t_object.capital_gains)  # returns blank
    #print(t_object.cash_flow)  # returns table 56 rows, 3 columns
    #print(t_object.dividends.values)  # returns blank
    #print(t_object.earnings_dates)  # returns table of earnings dates (EPS Estimate, EPS Actual, Surprise %)
    #print(t_object.financials)  # returns table 45 rows, 3 columns

    #print(t_object.history(period="max"))  # returns table 3000+ rows, 7 columns
    #print(t_object.history(start="2021-01-01", end="2021-01-10", interval="1d"))  # example of calling history

    #print(t_object.history_metadata)  # returns list and table 5 rows, 6 columns
    #print(t_object.income_stmt)  # returns table 45 rows, 3 columns

    #print(t_object.institutional_holders)  # returns table 10 rows, 5 columns
    #print(t_object.major_holders)  # returns basic table 4 deep
    #print(t_object.mutualfund_holders)  # returns table of 10 rows, 5 columns
    #print(get_holders(c_ticker[0][0])) # << this gives same output as the 3 above

    #print(t_object.news)  # returns a few related news articles, title, publisher, link

    # print(t_object.option_chain('2021-10-15'))
    # get option chain for specific expiration
    # opt = msft.option_chain('YYYY-MM-DD')
    # data available via: opt.calls, opt.puts
    #print(t_object.options)  # returns list of dates to use in option_chain (19 dates for example)
    #print(t_object.option_chain('2024-01-12'))  # returns table of 101x14, and table of 79x14 and metadata list

    #print(t_object.quarterly_balance_sheet)  # returns table 78 rows, 4 columns
    #print(t_object.quarterly_cash_flow)  # returns table 53 rows, 4 columns
    #print(t_object.quarterly_financials)  # returns table 46 rows, 4 columns
    #print(t_object.quarterly_income_stmt)  # returns table 46 rows, 4 columns
    #print(t_object.splits)  # returns table of splits
    #print(t_object.get_shares_full(start="2022-01-01", end=None))  # returns table

    # todo get list of all ticker based functions in ticker_and_indexes.py << lewis job

    #input("FINISHED.")
    #print(get_ticker_history("tsla", datetime.now()-timedelta(days=1), datetime.now(), "1d", "1m"))


    #print(get_yf_rss('tsla'))

    # get live price of apple
    #print(get_live_price('aapl'))


    #url = "https://www.google.com/finance/quote/TSLA:NASDAQ"
    #print(get(url).text)

    # live price sources:
    # https://www.google.com/finance/quote/TSLA:NASDAQ
    # https://finance.yahoo.com/quote/TSLA?p=TSLA&.tsrc=fin-srch
