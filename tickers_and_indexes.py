import requests
import pandas as pd
import ftplib
import io
import re
import json
import datetime
import warnings

# file of functions to pull tickers and indexes from various sources
# MODIFIED FROM YAHOO-FIN LIBRARY AT: https://pypi.org/project/yahoo-fin/#history

warnings.simplefilter(action='ignore', category=FutureWarning)
default_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


try:
    from requests_html import HTMLSession
except Exception:
    print("""Warning - Certain functionality 
             requires requests_html, which is not installed.
             
             Install using: 
             pip install requests_html
             
             After installation, you may have to restart your Python session.""")

    
base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"


def build_url(ticker, start_date=None, end_date=None, interval="1d"):
    
    if end_date is None:  
        end_seconds = int(pd.Timestamp("now").timestamp())
    else:
        end_seconds = int(pd.Timestamp(end_date).timestamp())
        
    if start_date is None:
        start_seconds = 7223400
    else:
        start_seconds = int(pd.Timestamp(start_date).timestamp())
    
    site = base_url + ticker
    
    params = {"period1": start_seconds, "period2": end_seconds,
              "interval": interval.lower(), "events": "div,splits"}

    return site, params


def force_float(elt):
    try:
        return float(elt)
    except ValueError:
        return elt


def _convert_to_numeric(s):

    if "M" in s:
        s = s.strip("M")
        return force_float(s) * 1_000_000
    
    if "B" in s:
        s = s.strip("B")
        return force_float(s) * 1_000_000_000
    
    return force_float(s)


# todo make work
def get_ticker_history(ticker, start_date=None, end_date=None, index_as_date=True,
                       interval="1d", headers=default_headers):

    '''Downloads historical stock price data into a pandas data frame.  Interval
       must be "1d", "1wk", "1mo", or "1m" for daily, weekly, monthly, or minute data.
       Intraday minute data is limited to 7 days.
    
       @param: ticker
       @param: start_date = None
       @param: end_date = None
       @param: index_as_date = True
       @param: interval = "1d"
    '''
    
    if interval not in ("1d", "1wk", "1mo", "1m"):
        raise AssertionError("interval must be of of '1d', '1wk', '1mo', or '1m'")

    # build and connect to URL
    site, params = build_url(ticker, start_date, end_date, interval)
    print(site, params, headers)
    resp = requests.get(site, params=params, headers=headers)

    if not resp.ok:
        raise AssertionError(resp.json())

    # get JSON response
    data = resp.json()
    print(data)
    
    # get open / high / low / close data
    frame = pd.DataFrame(data["chart"]["result"][0]["indicators"]["quote"][0])
    print(frame)

    # get the date info
    temp_time = data["chart"]["result"][0]["timestamp"]

    if interval != "1m":
    
        # add in adjclose
        frame["adjclose"] = data["chart"]["result"][0]["indicators"]["adjclose"][0]["adjclose"]   
        frame.index = pd.to_datetime(temp_time, unit = "s")
        frame.index = frame.index.map(lambda dt: dt.floor("d"))
        frame = frame[["open", "high", "low", "close", "adjclose", "volume"]]
    else:

        frame.index = pd.to_datetime(temp_time, unit = "s")
        frame = frame[["open", "high", "low", "close", "volume"]]
        
    frame['ticker'] = ticker.upper()
    
    if not index_as_date:  
        frame = frame.reset_index()
        frame.rename(columns = {"index": "date"}, inplace = True)
        
    return frame


def tickers_sp500():  # TODO ADD PERIOD INDEX FUND CHECK
    # Downloads list of tickers currently listed in the S&P 500
    # get list of all S&P 500 stocks
    sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
    sp_tickers = []
    for i in range(len(sp500)):
        sp_tickers.append(f"{sp500.values[i][0]}§{sp500.values[i][1]}§{sp500.values[i][2]}§"
                          f" {sp500.values[i][3]}§{sp500.values[i][4]}§{sp500.values[i][6]}")

    return sp_tickers


def _nasdaq_trader(search_param):
    # Downloads list of tickers

    ftp = ftplib.FTP("ftp.nasdaqtrader.com")
    ftp.login()
    ftp.cwd("SymbolDirectory")

    r = io.BytesIO()
    ftp.retrbinary(f'RETR {search_param}.txt', r.write)

    info = r.getvalue().decode()
    splits = info.split("|")

    tickers = [x for x in splits if len(x) > 1]
    ticker_data = []
    for i in range(len(tickers)-4):
        if tickers[i] == "100" and "-" in tickers[i+2]:
            stock_ticker = tickers[i+1].split('\r\n')[1]
            stock_name = tickers[i+2].split(" - ")[0]
            stock_type = str(tickers[i+2].split(" - ")[1:])[2:-2]
            ticker_data.append(f"{stock_ticker}§{stock_name}§{stock_type}")
        elif tickers[i] == "100" and "-" not in tickers[i+2] and "test stock" not in tickers[i+2].lower():
            stock_ticker = tickers[i+1].split('\r\n')[1]
            ticker_data.append(f"{stock_ticker}§{tickers[i+2]}")

    return ticker_data


def tickers_nasdaq():  # Nasdaq stocks
    return _nasdaq_trader("nasdaqlisted")


def tickers_us_other():  # Nasdaq other, funds, etfs, etc.
    return _nasdaq_trader("otherlisted")
    

def tickers_dow():  # Dow_Jones_Industrial_Average
    site = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
    table = pd.read_html(site, attrs={"id": "constituents"})[0]
    dow_tickers = []
    for i in range(len(table)):
        dow_tickers.append(f"{table.values[i][2]}§{table.values[i][0]}§{table.values[i][6]}§{table.values[i][1]}§"
                           f"{table.values[i][3]}")

    return dow_tickers    
    

#def tickers_ibovespa():
#
#    '''Downloads list of currently traded tickers on the Ibovespa, Brazil'''
#
#    table = pd.read_html("https://pt.wikipedia.org/wiki/Lista_de_companhias_citadas_no_Ibovespa")[0]
#    table.columns = ["Symbol", "Share", "Sector", "Type", "Site"]
#    print(table)
#
#    ibovespa_tickers = sorted(table.Symbol.tolist())
#
#    return ibovespa_tickers


def tickers_nifty50():  # NIFTY 50, India
    site = "https://en.wikipedia.org/wiki/NIFTY_50"
    table = pd.read_html(site, attrs={"id": "constituents"})[0]
    nifty50 = []
    for i in range(len(table)):
        nifty50.append(f"{table.values[i][1]}§{table.values[i][0]}§{table.values[i][2]}")

    return nifty50


def tickers_ftse100():  # UK 100
    table = pd.read_html("https://en.wikipedia.org/wiki/FTSE_100_Index", attrs={"id": "constituents"})[0]
    ftse100 = []
    for i in range(len(table)):
        ftse100.append(f"{table.values[i][1]}§{table.values[i][0]}§{table.values[i][2]}")

    return ftse100
    

def tickers_ftse250():  # UK 250
    table = pd.read_html("https://en.wikipedia.org/wiki/FTSE_250_Index", attrs={"id": "constituents"})[0]
    ftse250 = []
    for i in range(len(table)):
        ftse250.append(f"{table.values[i][1]}§{table.values[i][0]}§{table.values[i][2]}")

    return ftse250


def _site_scraper(site):
    tables = pd.read_html(requests.get(site, headers={'User-agent': 'Mozilla/5.0'}).text)
    data = {}
    for table in tables:
        for value in table.values:
            data.update({value[0]: str(value[1:])[2:-2]})

    return data


def get_ticker_data(ticker):
    # Scrapes data elements found on Yahoo Finance's quote page
    site = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}"
    return _site_scraper(site)


def get_ticker_stats(ticker):
    # Scrapes information from the statistics tab on Yahoo Finance
    stats_site = f"https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}"
    return _site_scraper(stats_site)


def _parse_json(url, headers={'User-agent': 'Mozilla/5.0'}):
    html = requests.get(url=url, headers=headers).text
    print(html)
    input()

    json_str = html.split('root.App.main =')[1].split(
        '(this)')[0].split(';\n}')[0].strip()
    
    try:
        data = json.loads(json_str)[
            'context']['dispatcher']['stores']['QuoteSummaryStore']
    except:
        return '{}'
    else:
        # return data
        new_data = json.dumps(data).replace('{}', 'null')
        new_data = re.sub(r'\{[\'|\"]raw[\'|\"]:(.*?),(.*?)}', r'\1', new_data)

        json_info = json.loads(new_data)

        return json_info


def _parse_table(json_info):

    df = pd.DataFrame(json_info)
    
    if df.empty:
        return df
    
    del df["maxAge"]

    df.set_index("endDate", inplace=True)
    df.index = pd.to_datetime(df.index, unit="s")
 
    df = df.transpose()
    df.index.name = "Breakdown"

    return df


def get_ticker_profile(ticker):
    prof_site = f"https://finance.yahoo.com/quote/{ticker}/profile?p={ticker}"
    return _site_scraper(prof_site)


# todo make work
def get_income_statement(ticker, yearly=True):
    #inc_site = f"https://finance.yahoo.com/quote/{ticker}/financials?p={ticker}"
    #return _site_scraper(inc_site)

    
    '''Scrape income statement from Yahoo Finance for a given ticker
    
       @param: ticker
    '''

    json_info = _parse_json(f"https://finance.yahoo.com/quote/{ticker}/financials?p={ticker}")
    
    if yearly:
        temp = json_info["incomeStatementHistory"]["incomeStatementHistory"]
    else:
        temp = json_info["incomeStatementHistoryQuarterly"]["incomeStatementHistory"]
    
    return _parse_table(temp)      
        

def get_balance_sheet(ticker, yearly=True):
    
    '''Scrapes balance sheet from Yahoo Finance for an input ticker 
    
       @param: ticker
    '''    

    json_info = _parse_json(f"https://finance.yahoo.com/quote/{ticker}/balance-sheet?p={ticker}")
    
    try:
        if yearly:
            temp = json_info["balanceSheetHistory"]["balanceSheetStatements"]
        else:
            temp = json_info["balanceSheetHistoryQuarterly"]["balanceSheetStatements"]
    except:
        temp = []
        
    return _parse_table(temp)      


def get_cash_flow(ticker, yearly=True):
    
    '''Scrapes the cash flow statement from Yahoo Finance for an input ticker 
    
       @param: ticker
    '''

    json_info = _parse_json(f"https://finance.yahoo.com/quote/{ticker}/cash-flow?p={ticker}")
    
    if yearly:
        temp = json_info["cashflowStatementHistory"]["cashflowStatements"]
    else:
        temp = json_info["cashflowStatementHistoryQuarterly"]["cashflowStatements"]
        
    return _parse_table(temp)      


def get_financials(ticker, yearly=True, quarterly=True):

    '''Scrapes financials data from Yahoo Finance for an input ticker, including
       balance sheet, cash flow statement, and income statement.  Returns dictionary
       of results.
    
       @param: ticker
       @param: yearly = True
       @param: quarterly = True
    '''

    if not yearly and not quarterly:
        raise AssertionError("yearly or quarterly must be True")

    json_info = _parse_json(f"https://finance.yahoo.com/quote/{ticker}/financials?p={ticker}")
    
    result = {}
    
    if yearly:

        temp = json_info["incomeStatementHistory"]["incomeStatementHistory"]
        table = _parse_table(temp)
        result["yearly_income_statement"] = table
    
        temp = json_info["balanceSheetHistory"]["balanceSheetStatements"]
        table = _parse_table(temp)
        result["yearly_balance_sheet"] = table
        
        temp = json_info["cashflowStatementHistory"]["cashflowStatements"]
        table = _parse_table(temp)
        result["yearly_cash_flow"] = table

    if quarterly:
        temp = json_info["incomeStatementHistoryQuarterly"]["incomeStatementHistory"]
        table = _parse_table(temp)
        result["quarterly_income_statement"] = table
    
        temp = json_info["balanceSheetHistoryQuarterly"]["balanceSheetStatements"]
        table = _parse_table(temp)
        result["quarterly_balance_sheet"] = table
        
        temp = json_info["cashflowStatementHistoryQuarterly"]["cashflowStatements"]
        table = _parse_table(temp)
        result["quarterly_cash_flow"] = table

    return result


def get_holders(ticker, headers={'User-agent': 'Mozilla/5.0'}):
    
    '''Scrapes the Holders page from Yahoo Finance for an input ticker 
    
       @param: ticker
    '''    

    holders_site = f"https://finance.yahoo.com/quote/{ticker}/holders?p={ticker}"
        
    tables = pd.read_html(requests.get(holders_site, headers=headers).text)

    table_names = ["Major Holders" , "Direct Holders (Forms 3 and 4)" ,
                   "Top Institutional Holders" , "Top Mutual Fund Holders"]

    table_mapper = {key : val for key,val in zip(table_names , tables)}

    return table_mapper       


def get_analysts_info(ticker, headers = {'User-agent': 'Mozilla/5.0'}):
    
    '''Scrapes the Analysts page from Yahoo Finance for an input ticker 
    
       @param: ticker
    '''    

    analysts_site = f"https://finance.yahoo.com/quote/{ticker}/analysts?p={ticker}"
    
    tables = pd.read_html(requests.get(analysts_site, headers=headers).text)
    
    table_names = [table.columns[0] for table in tables]

    table_mapper = {key : val for key , val in zip(table_names , tables)}

    return table_mapper

    
def _raw_get_daily_info(site):
       
    session = HTMLSession()
    
    resp = session.get(site)
    
    tables = pd.read_html(resp.html.raw_html)  
    
    df = tables[0].copy()
    
    df.columns = tables[0].columns
    
    del df["52 Week Range"]
    
    df["% Change"] = df["% Change"].map(lambda x: float(x.strip("%+").replace(",", "")))

    fields_to_change = [x for x in df.columns.tolist() if "Vol" in x \
                        or x == "Market Cap"]
    
    for field in fields_to_change:
        
        if type(df[field][0]) == str:
            df[field] = df[field].map(_convert_to_numeric)
            
    session.close()
    
    return df
    

def get_day_most_active(count: int = 100):

    return _raw_get_daily_info(f"https://finance.yahoo.com/most-active?offset=0&count={count}")


def get_day_gainers(count: int = 100):

    return _raw_get_daily_info(f"https://finance.yahoo.com/gainers?offset=0&count={count}")


def get_day_losers(count: int = 100):

    return _raw_get_daily_info(f"https://finance.yahoo.com/losers?offset=0&count={count}")


def get_top_crypto():
    
    '''Gets the top 100 Cryptocurrencies by Market Cap'''      

    session = HTMLSession()
    
    resp = session.get("https://finance.yahoo.com/cryptocurrencies?offset=0&count=100")
    
    tables = pd.read_html(resp.html.raw_html)               
                    
    df = tables[0].copy()

    
    df["% Change"] = df["% Change"].map(lambda x: float(str(x).strip("%").\
                                                               strip("+").\
                                                               replace(",", "")))
    del df["52 Week Range"]
    del df["1 Day Chart"]
    
    fields_to_change = [x for x in df.columns.tolist() if "Volume" in x \
                        or x == "Market Cap" or x == "Circulating Supply"]
    
    for field in fields_to_change:
        
        if type(df[field][0]) == str:
            df[field] = df[field].map(lambda x: _convert_to_numeric(str(x)))

    session.close()        
                
    return df
                    
        
def get_dividends(ticker, start_date=None, end_date=None, index_as_date=True, headers=default_headers):
    '''Downloads historical dividend data into a pandas data frame.
    
       @param: ticker
       @param: start_date = None
       @param: end_date = None
       @param: index_as_date = True
    '''
    
    # build and connect to URL
    site, params = build_url(ticker, start_date, end_date, "1d")
    resp = requests.get(site, params=params, headers=headers)

    if not resp.ok:
        return pd.DataFrame()

    # get JSON response
    data = resp.json()
    
    # check if there is data available for dividends
    if "events" not in data["chart"]["result"][0] or "dividends" not in data["chart"]["result"][0]['events']:
        return pd.DataFrame()
    
    # get the dividend data
    frame = pd.DataFrame(data["chart"]["result"][0]['events']['dividends'])
    
    frame = frame.transpose()
        
    frame.index = pd.to_datetime(frame.index, unit = "s")
    frame.index = frame.index.map(lambda dt: dt.floor("d"))
    
    # sort in chronological order
    frame = frame.sort_index()
        
    frame['ticker'] = ticker.upper()
    
    # remove old date column
    frame = frame.drop(columns='date')
    
    frame = frame.rename({'amount': 'dividend'}, axis = 'columns')
    
    if not index_as_date:  
        frame = frame.reset_index()
        frame.rename(columns = {"index": "date"}, inplace = True)
        
    return frame


def get_splits(ticker, start_date=None, end_date=None, index_as_date=True, headers=default_headers):
    '''Downloads historical stock split data into a pandas data frame.
    
       @param: ticker
       @param: start_date = None
       @param: end_date = None
       @param: index_as_date = True
    '''
    
    # build and connect to URL
    site, params = build_url(ticker, start_date, end_date, "1d")
    resp = requests.get(site, params=params, headers=headers)

    if not resp.ok:
        raise AssertionError(resp.json())

    # get JSON response
    data = resp.json()
    
    # check if there is data available for splits
    if "splits" not in data["chart"]["result"][0]['events']:
        raise AssertionError("There is no data available on stock splits, or none have occured")
    
    # get the split data
    frame = pd.DataFrame(data["chart"]["result"][0]['events']['splits'])
    
    frame = frame.transpose()
        
    frame.index = pd.to_datetime(frame.index, unit = "s")
    frame.index = frame.index.map(lambda dt: dt.floor("d"))
    
    # sort in to chronological order
    frame = frame.sort_index()
        
    frame['ticker'] = ticker.upper()
    
    # remove unnecessary columns
    frame = frame.drop(columns=['date', 'denominator', 'numerator'])
    
    if not index_as_date:  
        frame = frame.reset_index()
        frame.rename(columns = {"index": "date"}, inplace = True)
        
    return frame
        

def get_earnings(ticker):
    
    '''Scrapes earnings data from Yahoo Finance for an input ticker 
    
       @param: ticker
    '''

    result = {
        "quarterly_results": pd.DataFrame(),
        "yearly_revenue_earnings": pd.DataFrame(),
        "quarterly_revenue_earnings": pd.DataFrame()
    }

    financials_site = "https://finance.yahoo.com/quote/" + ticker + \
        "/financials?p=" + ticker

    json_info = _parse_json(financials_site)

    if "earnings" not in json_info:
        return result

    temp = json_info["earnings"]

    if temp == None:
        return result
    
    result["quarterly_results"] = pd.DataFrame.from_dict(temp["earningsChart"]["quarterly"])
    
    result["yearly_revenue_earnings"] = pd.DataFrame.from_dict(temp["financialsChart"]["yearly"])
    
    result["quarterly_revenue_earnings"] = pd.DataFrame.from_dict(temp["financialsChart"]["quarterly"])
    
    return result


### Earnings functions
def _parse_earnings_json(url, headers=default_headers):
        resp = requests.get(url, headers=headers)
        
        content = resp.content.decode(encoding='utf-8', errors='strict')
        
        page_data = [row for row in content.split(
            '\n') if row.startswith('root.App.main = ')][0][:-1]
        
        page_data = page_data.split('root.App.main = ', 1)[1]
        
        return json.loads(page_data)


def get_next_earnings_date(ticker):
        
    base_earnings_url = 'https://finance.yahoo.com/quote'
    new_url = base_earnings_url + "/" + ticker

    parsed_result = _parse_earnings_json(new_url)
    
    temp = parsed_result['context']['dispatcher']['stores']['QuoteSummaryStore']['calendarEvents']['earnings']['earningsDate'][0]['raw']

    return datetime.datetime.fromtimestamp(temp)


def get_earnings_history(ticker):
    
        '''Inputs: @ticker
           Returns the earnings calendar history of the input ticker with 
           EPS actual vs. expected data.'''

        url = 'https://finance.yahoo.com/calendar/earnings?symbol=' + ticker
         
        result = _parse_earnings_json(url)
        
        return result["context"]["dispatcher"]["stores"]["ScreenerResultsStore"]["results"]["rows"]


def get_earnings_for_date(date, offset = 0, count = 1):

    '''Inputs: @date
       Returns a dictionary of stock tickers with earnings expected on the
       input date.  The dictionary contains the expected EPS values for each
       stock if available.'''
    
    base_earnings_url = 'https://finance.yahoo.com/calendar/earnings'
    
    if offset >= count:
        return []
    
    temp = pd.Timestamp(date)
    date = temp.strftime("%Y-%m-%d")

    dated_url = '{0}?day={1}&offset={2}&size={3}'.format(
        base_earnings_url, date, offset, 100)
    
    result = _parse_earnings_json(dated_url)
    
    stores = result['context']['dispatcher']['stores']
    
    earnings_count = stores['ScreenerCriteriaStore']['meta']['total']

    new_offset = offset + 100
    
    more_earnings = get_earnings_for_date(date, new_offset, earnings_count)
    
    current_earnings = stores['ScreenerResultsStore']['results']['rows']

    total_earnings = current_earnings + more_earnings

    return total_earnings


def get_earnings_in_date_range(start_date, end_date):

        '''Inputs: @start_date
                   @end_date
                   
           Returns the stock tickers with expected EPS data for all dates in the
           input range (inclusive of the start_date and end_date.'''
    
        earnings_data = []

        days_diff = pd.Timestamp(end_date) - pd.Timestamp(start_date)
        days_diff = days_diff.days

        current_date = pd.Timestamp(start_date)
        
        dates = [current_date + datetime.timedelta(diff) for diff in range(days_diff + 1)]
        dates = [d.strftime("%Y-%m-%d") for d in dates]
 
        i = 0
        while i < len(dates):
            try:
                earnings_data += get_earnings_for_date(dates[i])
            except Exception:
                pass
            
            i += 1
            
        return earnings_data


def get_currencies(headers={'User-agent': 'Mozilla/5.0'}):
    
    '''Returns the currencies table from Yahoo Finance'''
    
    site = "https://finance.yahoo.com/currencies"
    tables = pd.read_html(requests.get(site, headers=headers).text)
    
    result = tables[0]
    
    return result


def get_futures(headers={'User-agent': 'Mozilla/5.0'}):
    
    '''Returns the futures table from Yahoo Finance'''
    
    site = "https://finance.yahoo.com/commodities"
    tables = pd.read_html(requests.get(site, headers=headers).text)
    
    result = tables[0]
    
    return result


def get_undervalued_large_caps(headers = {'User-agent': 'Mozilla/5.0'}):
    
    '''Returns the undervalued large caps table from Yahoo Finance'''
    
    site = "https://finance.yahoo.com/screener/predefined/undervalued_large_caps?offset=0&count=100"
    
    tables = pd.read_html(requests.get(site, headers=headers).text)
    
    result = tables[0]
    
    return result


def get_quote_data(ticker, headers=default_headers):
    
    '''Inputs: @ticker
    
       Returns a dictionary containing over 70 elements corresponding to the 
       input ticker, including company name, book value, moving average data,
       pre-market / post-market price (when applicable), and more.'''

    site = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}"
    resp = requests.get(site, headers=headers)
    
    if not resp.ok:
        raise AssertionError("""Invalid response from server.  Check if ticker is
                              valid.""")

    json_result = resp.json()
    info = json_result["quoteResponse"]["result"]
    
    return info[0]


def get_premarket_price(ticker):

    '''Inputs: @ticker
    
       Returns the current pre-market price of the input ticker
       (returns value if pre-market price is available.'''
    
    quote_data = get_quote_data(ticker)
    
    if "preMarketPrice" in quote_data:
        return quote_data["preMarketPrice"]
        
    raise AssertionError("Premarket price not currently available.")


def get_postmarket_price(ticker):

    '''Inputs: @ticker
    
       Returns the current post-market price of the input ticker
       (returns value if pre-market price is available.'''
    
    quote_data = get_quote_data(ticker)
    
    if "postMarketPrice" in quote_data:
        return quote_data["postMarketPrice"]
    
    raise AssertionError("Postmarket price not currently available.")
    

# Company Information Functions
def get_company_info(ticker):
    '''Scrape the company information for a ticker

       @param: ticker
    '''
    site = f"https://finance.yahoo.com/quote/{ticker}/profile?p={ticker}"
    json_info = _parse_json(site)
    json_info = json_info["assetProfile"]
    info_frame = pd.DataFrame.from_dict(json_info, orient="index", columns=["Value"])
    info_frame = info_frame.drop("companyOfficers", axis="index")
    info_frame.index.name = "Breakdown"
    return info_frame


def get_company_officers(ticker):
    '''Scrape the company information and return a table of the officers

       @param: ticker
    '''
    site = f"https://finance.yahoo.com/quote/{ticker}/profile?p={ticker}"
    json_info = _parse_json(site)
    json_info = json_info["assetProfile"]["companyOfficers"]
    info_frame = pd.DataFrame.from_dict(json_info)
    info_frame = info_frame.set_index("name")
    return info_frame