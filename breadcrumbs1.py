from firehose import get_yf_rss
from stock_info import *
from options import *

#print(get_yf_rss('tsla'))

# get live price of apple
#print(get_live_price('aapl'))


#print(tickers_sp500())


from requests import get

url = "https://www.google.com/finance/quote/TSLA:NASDAQ"
print(get(url).text)


# live price sources:
# https://www.google.com/finance/quote/TSLA:NASDAQ
# https://finance.yahoo.com/quote/TSLA?p=TSLA&.tsrc=fin-srch
