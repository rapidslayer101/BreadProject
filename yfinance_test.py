import yfinance as yf

# test file for understanding how to use yfinance
# todo finish testing and remove redundant file

msft = yf.Ticker("TSLA")

# get all stock info
print(msft.info)
print(msft)

input()
print(msft.fast_info)

# get historical market data
hist = msft.history(period="1mo")

# show meta information about the history (requires history() to be called first)
print(msft.history_metadata)
print(msft.history_metadata['regularMarketPrice'])

# show actions (dividends, splits, capital gains)
print(msft.actions)
print(msft.dividends)
print(msft.splits)
print(msft.capital_gains)  # only for mutual funds & etfs

input()
# show share count
msft.get_shares_full(start="2022-01-01", end=None)

# show financials:
# - income statement
msft.income_stmt
msft.quarterly_income_stmt
# - balance sheet
msft.balance_sheet
msft.quarterly_balance_sheet
# - cash flow statement
msft.cashflow
msft.quarterly_cashflow
# see `Ticker.get_income_stmt()` for more options

# show holders
msft.major_holders
msft.institutional_holders
msft.mutualfund_holders

# Show future and historic earnings dates, returns at most next 4 quarters and last 8 quarters by default.
# Note: If more are needed use msft.get_earnings_dates(limit=XX) with increased limit argument.
msft.earnings_dates

# show ISIN code - *experimental*
# ISIN = International Securities Identification Number
msft.isin

# show options expirations
msft.options

# show news
msft.news

# get option chain for specific expiration
#opt = msft.option_chain('YYYY-MM-DD')
# data available via: opt.calls, opt.puts