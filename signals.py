# _*_ coding: utf-8 -*-

from blinker import signal

after_post_tickers = signal('after-post-tickers')

@after_post_tickers.connect
def download_prices(sender,**kwargs):
    from tasks import add_ticker_prices
    tickers = kwargs.get("tickers")
    tickers = [(tk.id,tk.symbol) for tk in tickers]
    add_ticker_prices(full=True,tickers=tickers)
