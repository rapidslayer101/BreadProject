import tickers_and_cache as tnc

while True:
    #c_name = input("Ticker name: ")
    c_name = ["Rolls-royce", "Tesco"]
    t_objects = tnc.TNS(c_name, other=False).get_objects()
    if not t_objects:
        print("Ticker not found: TNS failed to resolve ticker")
    else:
        break

function_list = [function for function in dir(tnc) if not function.startswith('_')]
print(function_list)

print(t_objects)
input()

# todo list of functions that are not linked to a ticker
#print(get_day_trending_tickers())
#print(get_day_top_futures())
#print(get_day_highest_open_interest())
#print(get_day_highest_implied_volatility())
#print(get_day_top_world_indices())
#print(get_day_top_forex_rates())
#print(get_day_top_us_bonds())
#print(get_day_top_crypto())
#print(get_currencies())
#print(get_futures())

# todo list of functions that ONLY SHOW US REGION
#print(get_day_most_active())
#print(get_day_gainers())
#print(get_day_losers())
#print(get_day_top_etfs())
#print(get_day_top_mutual())
#print(get_undervalued_large_caps())


c_ticker, c_index = tns(c_name)
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

t_object = Ticker(c_ticker[0][0])
print(t_object.get_news())
input()

#input("Enter to fetch all data: ")
t_object = YF_ticker(c_ticker[0][0])

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

#print(get_earnings_history()) + print(t_object.earnings_dates)  # todo use this to create earnings history table
#print(get_analysts_info())



# get live price of apple  # todo make a function to get live price of ticker
#print(get_live_price('aapl'))

# live price sources:
# https://www.google.com/finance/quote/TSLA:NASDAQ
# https://finance.yahoo.com/quote/TSLA?p=TSLA&.tsrc=fin-srch