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


def refresh_ticker_data(file, refresh_days):
    if not exists(f"TickerData/{file}.txt"):
        print(f"Downloading {file} tickers...")
        with open(f"TickerData/{file}.txt", "w", encoding="utf-8") as f:
            f.write(f"# reload+after+{datetime.now()+timedelta(days=refresh_days)}\n")
            if file == "sp_500":
                for ticker in tickers_sp500():
                    f.write(f"{ticker}\n")
            elif file == "nasdaq":
                for ticker in tickers_nasdaq():
                    f.write(f"{ticker}\n")
            elif file == "nasdaq_other":
                for ticker in tickers_us_other():
                    f.write(f"{ticker}\n")
    else:
        with open(f"TickerData/{file}.txt", "r", encoding="utf-8") as f:
            file_time = datetime.strptime(f.readline().split("+")[2].replace("\n", ""), "%Y-%m-%d %H:%M:%S.%f")
            if file_time < datetime.now():
                with open(f"TickerData/{file}.txt", "w", encoding="utf-8") as f:
                    f.write(f"# reload+after+{datetime.now()+timedelta(days=refresh_days)}\n")
                    if file == "sp_500":
                        for ticker in tickers_sp500():
                            f.write(f"{ticker}\n")
                    elif file == "nasdaq":
                        for ticker in tickers_nasdaq():
                            f.write(f"{ticker}\n")
                    elif file == "nasdaq_other":
                        for ticker in tickers_us_other():
                            f.write(f"{ticker}\n")
                print(f"Found and refreshed {file} tickers...")
            else:
                print(f"Found {file} tickers...")


refresh_ticker_data("sp_500", 7)
refresh_ticker_data("nasdaq", 7)
refresh_ticker_data("nasdaq_other", 7)


input()
print(tickers_dow())



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
