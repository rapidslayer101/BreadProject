from os.path import exists
from os import mkdir
from stock_info import *
from options import *

"""BELOW IS THE LOADER SYSTEM FOR TICKER DATA"""

if not exists("TickerData"):
    mkdir("TickerData")
    print("Created TickerData directory...")
else:
    print("Found TickerData directory...")

# load sp500 tickers
if not exists("TickerData/sp500.txt"):
    print("Downloading sp500 tickers...")
    with open("TickerData/sp500.txt", "w", encoding="utf-8") as f:
        for ticker in tickers_sp500():
            f.write(f"{ticker}\n")
else:
    print("Found sp500 tickers...")


# load nasdaq tickers   # todo make work <---
if not exists("TickerData/nasdaq.txt"):
    print("Downloading nasdaq tickers...")
    with open("TickerData/nasdaq.txt", "w", encoding="utf-8") as f:
        for ticker in tickers_nasdaq():
            f.write(f"{ticker}\n")
else:
    print("Found nasdaq tickers...")


# load nasdaq tickers   # todo make work <---
if not exists("TickerData/other.txt"):
    print("Downloading other tickers...")
    with open("TickerData/other.txt", "w", encoding="utf-8") as f:
        for ticker in tickers_us_other():
            f.write(f"{ticker}\n")
else:
    print("Found other tickers...")



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
