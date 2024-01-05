from tickers_and_indexes import *
from datetime import datetime, timedelta
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


def tns(name):  # ticker name system  # todo work in progress
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

    return related_tickers, relevant_indexes


def _ticker_info_writer_(_ticker):
    t_object = yf.Ticker(_ticker)
    t_info = t_object.info
    ticker_profile = {}
    with open(f"TickerData/Tickers/{_ticker}/profile.txt", "w", encoding="utf-8") as f:
        f.write(f"# reload+after+{datetime.now() + timedelta(days=14)}\n")
        for key in t_info.keys():
            if key == "previousClose":
                break
            f.write(f"{key}§{t_info[key]}\n")
            ticker_profile.update({key: t_info[key]})
        keys = ["forwardEps", "pegRatio", "lastDividendValue", "currency", "exchange", "quoteType", "shortName",
                "longName", "firstTradeDateEpochUtc", "timeZoneFullName", "timeZoneShortName", "uuid",
                "messageBoardId", "gmtOffSetMilliseconds", "targetHighPrice", "targetLowPrice", "targetMeanPrice",
                "targetMedianPrice", "recommendationMean", "recommendationKey", "numberOfAnalystOpinions",
                "quickRatio", "earningsGrowth", "grossMargins", "ebitdaMargins", "trailingPegRatio"]
        for key in keys:
            try:
                f.write(f"{key}§{t_info[key]}\n")
                ticker_profile.update({key: t_info[key]})
            except KeyError:
                print(f"KeyError: {key}")
    return ticker_profile


# loads company profile from cache or downloads it, returns profile data
def load_ticker_info(_ticker):
    if exists(f"TickerData/Tickers/{_ticker}/profile.txt"):
        with open(f"TickerData/Tickers/{_ticker}/profile.txt", "r", encoding="utf-8") as f:
            file_time = datetime.strptime(f.readline().split("+")[2].replace("\n", ""), "%Y-%m-%d %H:%M:%S.%f")
            if file_time < datetime.now():
                ticker_profile = _ticker_info_writer_(_ticker)
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


# todo check profile formats for ETF, FUND, COMMON STOCK, SHARES
# todo basically check if more or less data is provided than the predefined list in _ticker_info_writer_
# todo do not wish to miss data, MAKE EXCLUSION LIST RATHER THAN INCLUSION LIST
# lse = ["SHRS", "ETFS", "DPRS", "OTHR"]
# nasdaq = ??? a mess of like 400 different types, more research needed

data_set = set()
for ticker in nasdaq:
    try:
        t_type = ticker[2]
        if t_type not in []:
            print(t_type)
            data_set.add(t_type)
            #print(ticker)
    except:
        pass
print(data_set)


input()


# the below block of code is TNS logic
while True:
    c_name = input("Ticker name: ")
    ticker, index = tns(c_name)
    if not ticker:
        print("Ticker not found: TNS failed to resolve ticker")
    else:
        break

ticker_live = get_ticker_data(ticker[0][0])
# extra ticker name system code to try to detect if invalid ticker is returned from TNS
try:
    ticker_live['Open']
except KeyError:
    fixed = False
    for key in ticker_live.keys():
        if re.search(r"\b"+re.escape(c_name.lower())+r"\b", ticker_live[key].lower()):
            print(f"TNS Fixed: {ticker[0][0]} --> {key}")
            ticker = [[key, ticker_live[key]]]
            ticker_live = get_ticker_data(ticker[0][0])
            fixed = True
            break
    if not fixed:
        print(ticker_live)
        exit(f"Ticker error: TNS failed to resolve ticker")
# the above block of code is TNS logic


print(ticker[0][0], index)
print(get_ticker_data(ticker[0][0]))
print(get_ticker_stats(ticker[0][0]))
ticker_data = load_ticker_info(ticker[0][0])  # loads from cache or generates cache

input("Enter to fetch all data: ")
t_object = yf.Ticker(ticker[0][0])
print(t_object.news)  # << live

input()
print(t_object.earnings_dates)
print(t_object.dividends.values)
print(t_object.actions)
print(t_object.balance_sheet)
print(t_object.capital_gains)  # ???
print(t_object.cash_flow)
print(t_object.financials)
print(t_object.history_metadata)
print(t_object.income_stmt)
print(t_object.institutional_holders)
print(t_object.mutualfund_holders)
print(t_object.quarterly_balance_sheet)
print(t_object.quarterly_cash_flow)
print(t_object.quarterly_financials)
print(t_object.quarterly_income_stmt)
print(t_object.splits)

print(ticker_data)

input()
print(get_ticker_history("tsla", datetime.now()-timedelta(days=1), datetime.now(), "1d", "1m"))



#print(get_yf_rss('tsla'))

# get live price of apple
#print(get_live_price('aapl'))


#print(tickers_sp500())


#url = "https://www.google.com/finance/quote/TSLA:NASDAQ"
#print(get(url).text)


# live price sources:
# https://www.google.com/finance/quote/TSLA:NASDAQ
# https://finance.yahoo.com/quote/TSLA?p=TSLA&.tsrc=fin-srch
