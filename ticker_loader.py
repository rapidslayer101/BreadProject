from os.path import exists
from os import mkdir
from tickers_and_indexes import *
from datetime import datetime, timedelta
from options import *

# File to load TICKERS, INDEXES and COMPANIES so that AI can link them together
# This file should be called when the program starts


if not exists("TickerData"):
    mkdir("TickerData")
    print("Created TickerData directory...")
else:
    print("Found TickerData directory...")


def _loader_(file, refresh_days):
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
        ticker_info = _loader_(file, refresh_days)
    else:
        with open(f"TickerData/{file}.txt", "r", encoding="utf-8") as f:
            file_time = datetime.strptime(f.readline().split("+")[2].replace("\n", ""), "%Y-%m-%d %H:%M:%S.%f")
            if file_time < datetime.now():
                ticker_info = _loader_(file, refresh_days)
                print(f"Found and refreshed {file} tickers...")
            else:
                print(f"Found {file} tickers...")
                ticker_info = []
                for ticker in f.readlines():
                    ticker_info.append(ticker.replace("\n", "").split("§"))
    return ticker_info

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

#print(get_ticker_data("tsla"))
#print(get_ticker_stats("tsla"))
print(get_ticker_profile("tsla"))

#print(get_ticker_history("tsla", datetime.now()-timedelta(days=1), datetime.now(),
#                         "1d", "1m"))


input()




#print(get_yf_rss('tsla'))

# get live price of apple
#print(get_live_price('aapl'))


#print(tickers_sp500())


from requests import get

#url = "https://www.google.com/finance/quote/TSLA:NASDAQ"
#print(get(url).text)


# live price sources:
# https://www.google.com/finance/quote/TSLA:NASDAQ
# https://finance.yahoo.com/quote/TSLA?p=TSLA&.tsrc=fin-srch
