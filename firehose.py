import feedparser


# TODO LIBRARY FOR RSS FEEDS

yf_rss_url = 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=%s&region=US&lang=en-US'


def get_yf_rss(ticker):
    print(yf_rss_url % ticker)
    feed = feedparser.parse(yf_rss_url % ticker)

    return feed.entries

