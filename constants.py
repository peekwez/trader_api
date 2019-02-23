# _*_ coding: utf-8 -*-

import datetime
import tempfile

from models import Price, Ticker



OPERATORS = (
    "__eq",
    "__gt",
    "__gte",
    "__lt",
    "__lte",
)

AGGREGATORS = (
    "avg__",
    "min__",
    "max__",
)

TICKER_COLUMNS = {
    "symbol": Ticker.symbol.in_,
    "sector": Ticker.sector.like,
    "industry": Ticker.industry.like,
    "market": Ticker.market.in_,
    "type": Ticker.type.in_,
    "exchange": Ticker.exchange.in_,
}

PRICE_COLUMNS = {
    "date":Price.date,
    "open":Price.open,
    "low":Price.low,
    "high":Price.high,
    "close":Price.close,
    "adj_close":Price.adj_close,
    "volume":Price.volume,
    "dollar_volume":Price.dollar_volume,
}

UPDATE_TIME = datetime.time(7,30,0)

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

BANNER  = "\n  Trader-Data Ipython Shell\n"
BANNER += 25*"-" + "\n"
BANNER += " App     :: app, db, jwt, ma \n"
BANNER += " Models  :: Ticker, Price, UpdatesLog, User, TokenBlackList \n"
BANNER += " Tasks   :: add_prices, add_ticker_prices \n"
BANNER += " Modules :: utils \n"

TMP_FD, TMP_PATH = tempfile.mkstemp()
