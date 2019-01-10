# _*_ coding: utf-8 -*-

from models import Price, Ticker

import datetime


OPERATORS = (
    "",
    "__gt",
    "__gte",
    "__lt",
    "__lte",
)

TICKER_COLUMNS = {
    "symbol": Ticker.symbol.in_,
    "sector": Ticker.sector.like,
    "industry": Ticker.sector.like,
    "market": Ticker.market.in_,
    "type": Ticker.type.in_,
}

PRICE_COLUMNS = {
    "date":Price.date,
    "open":Price.open,
    "low":Price.low,
    "high":Price.high,
    "close":Price.open,
    "adj_close":Price.adj_close,
    "volume":Price.volume,
}

UPDATE_TIME = datetime.time(23,0,0)

TICKER_LIST = {
    "filename": "assets/tickers.xls",
    "sheets": (
        "nasdaq","nyse","amex","tmx",
    ),
    "columns":(
        "Name","Exchange","Symbol",
        "Sector","Industry","Value",
    )
}

CA_LIMIT = 150*1e6 # 150 million - Canada
US_LIMIT = 300*1e6 # 300 million - United States

VALUATION_LIMIT = {
    "nasdaq": US_LIMIT,
    "nyse": US_LIMIT,
    "amex": US_LIMIT,
    "tmx": CA_LIMIT,
}
