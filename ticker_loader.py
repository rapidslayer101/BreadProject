from os.path import exists
from os import mkdir, rename
from tickers_and_indexes import *
from datetime import datetime, timedelta
from pandas import read_excel

# File to load TICKERS, INDEXES and COMPANIES so that AI can link them together
# This file should be called when the program starts


if not exists("TickerData"):
    mkdir("TickerData")
    print("Created TickerData directory...")
else:
    print("Found TickerData directory...")


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

# todo UK tickers list  -- https://www.londonstockexchange.com/reports?tab=instruments
# the UK stock list is updated once a month in the first week of the month

tickers = [nasdaq, nasdaq_other, lse, lse_eq]
indexes = {'sp_500': sp_500, 'dow_jones': dow_jones, 'nifty50': nifty50, 'ftse100': ftse100, 'ftse250': ftse250}


print("Loaded tickers and indexes successfully...\n-------------------------------------------")


def tns(name):  # ticker name system  # todo work in progress
    name = name.lower()
    related_tickers = []
    counter = 0
    for ticker_list in tickers:
        counter += 1
        for ticker in ticker_list:
            if f"{name} " in ticker[1].lower():
                related_tickers.append([ticker[0], ticker[1]])
                #print(ticker)
            if f"{name}, " in ticker[1].lower():
                #print(ticker)
                related_tickers.append([ticker[0], ticker[1]])

    relevant_indexes = []
    for ticker in related_tickers:
        for key in indexes.keys():
            for _ticker in indexes[key]:
                if ticker[0] == _ticker[0]:
                    relevant_indexes.append(key)
    return related_tickers, relevant_indexes


print(tns("Tesla"))
print(tns("Microsoft"))
print(tns("Apple"))
print(tns("Alphabet"))
print(tns("Amazon"))
print(tns("Rolls-Royce"))

while True:
    print(tns(input("Ticker name: ")))


print(get_ticker_data("amd"))
print(get_ticker_stats("amd"))
print(get_ticker_profile("amd"))

#print(get_ticker_history("tsla", datetime.now()-timedelta(days=1), datetime.now(),
#                         "1d", "1m"))


input()




#print(get_yf_rss('tsla'))

# get live price of apple
#print(get_live_price('aapl'))


#print(tickers_sp500())


#url = "https://www.google.com/finance/quote/TSLA:NASDAQ"
#print(get(url).text)


# live price sources:
# https://www.google.com/finance/quote/TSLA:NASDAQ
# https://finance.yahoo.com/quote/TSLA?p=TSLA&.tsrc=fin-srch
