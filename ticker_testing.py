import tickers_and_cache as tnc

# This file is for testing the ticker data and cache functions
print(tnc.get_earnings_in_date_range_us("2023-01-05", "2023-01-10"))
input()

while True:
    c_list = ["Rolls-royce", "Tesco"]
    t_objects, t_results = tnc.TNS(c_list).get_objects_and_results()
    if not t_objects:
        print("Ticker not found: TNS failed to resolve ticker")
    else:
        break

for t in t_objects:
    print(t, t_objects[t].get_ticker_stats())
print(t_results)
input()

# todo redo list of functions that are not linked to a ticker
#print(tnc.get_day_trending_tickers())
#print(tnc.get_day_top_futures())
#print(tnc.get_day_highest_open_interest())
#print(tnc.get_day_highest_implied_volatility())
#print(tnc.get_day_top_world_indices())
#print(tnc.get_day_top_forex_rates())
#print(tnc.get_day_top_us_bonds())
#print(tnc.get_day_top_crypto())
#print(tnc.get_currencies())
#print(tnc.get_futures())
#print(tnc.get_day_most_active())
#print(tnc.get_day_gainers())
#print(tnc.get_day_losers())
#print(tnc.get_day_top_etfs())
#print(tnc.get_day_top_mutual())
#print(tnc.get_undervalued_large_caps())

# 4 functions that are linked to ticker
#print(tnc.get_ticker_stats("tsla"))
#print(tnc.get_ticker_data("tsla"))
#print(tnc.get_earnings_history()) + print(t_object.earnings_dates)  # todo use this to create earnings history table
#print(tnc.get_analysts_info())


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
#print(tnc.get_holders(c_ticker[0][0])) # << this gives same output as the 3 above

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

