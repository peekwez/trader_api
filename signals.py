# _*_ coding: utf-8 -*-

from models import Ticker, Price

def post_models_committed(sender, changes):
    tickers = []
    for model, change in changes:
        if isinstance(model,Ticker):
            if hasattr(model,'__commit_insert__') and change == "insert":
                ticker = model.__commit_insert__()
                tickers.append(ticker)

    if tickers:
        from tasks import add_ticker_prices
        add_ticker_prices(full=True,tickers=tickers)
