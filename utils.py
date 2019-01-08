# _*_ coding: utf-8 -*-

from flask import Flask
from models import db, Price, Ticker
from constants import OPERATORS, PRICE_COLUMNS, TICKER_COLUMNS, UPDATE_TIME

from pandas_datareader import data as pdr
from datetime import datetime, timedelta, time
import fix_yahoo_finance as yf

date = lambda x: datetime.strptime(x,'%Y-%m-%d')

def add_price_params(parser):

    # suffix for numerical and date queries
    operators = OPERATORS

    # add ticker symbol
    parser.add_argument("symbol", type=str, action="split", required=True)

    # add date parser
    for ops in operators:
        parser.add_argument("date{0}".format(ops), type=date)

    # add OHCL parser
    fields = ("open","low","high","close","adj_close","volume")
    for field in fields:
        for ops in operators:
            parser.add_argument("{0}{1}".format(field,ops), type=float)

    return parser

def comp(a,b,ops=None):

    # compare filters
    if ops == "gte":
        return a >= b
    elif ops == "gt":
        return a > b
    elif ops == "lte":
        return a <= b
    elif ops == "lt":
        return a < b
    else:
        return a == b

def get_ticker_filters(args):

    # get filter for tickers
    columns = TICKER_COLUMNS
    bools = ()
    for key in args.keys():
        if args.get(key) is not None:
            value = args.get(key).split(",")
            bools += columns[key](value),

    return bools

def get_price_filters(args):

    # get symbol ids
    symbol = args.get('symbol').split(',')
    ticker_id = Ticker.query.with_entities(
        Ticker.id
    ).filter(Ticker.symbol.in_(symbol))


    # build boolean for query
    bools = (
        Price.ticker_id.in_(ticker_id),
    )

    # get keys and columns to compare
    columns = PRICE_COLUMNS

    for key in args.keys():
        if key is not "symbol" and args.get(key) is not None:
            param, ops = key.split("__")
            value = args.get(key)
            column = columns[param]

            # compare and return boolean
            bool = comp(column,value,ops)

            # update boolean args
            bools += bool,

    return bools


def get_context(config_file="config"):

    # get a context for execution
    app = Flask(__name__)
    app.config.from_object(config_file)
    from models import db
    db.init_app(app)
    return app


def get_chunks(l,n):

    # chunk data for downloads
    for k in range(0,len(l),n):
        yield l[k:k+n]


def get_ticker_id(row,tkids):

    # get ticker id based on symbol
    key = row['symbol']
    return tkids[key]


def get_tickers():

    # get tickers
    try:
        tickers = Ticker.query.with_entities(
            Ticker.id,Ticker.symbol
        ).all()
    except:
        app = get_context()
        with app.app_context():
            tickers = Ticker.query.with_entities(
                Ticker.id,
                Ticker.symbol
            ).all()
    return tickers


def get_dates(full_update=False,offset=1):


    # daily updates
    date_0 = datetime.now() - timedelta(offset)
    date_1 = date_0 + timedelta(1)
    if full_update:
        year = date_1.year;
        date_0 = datetime(year-15,1,1)
        if date_1.time() < UPDATE_TIME:
            date_1 -= timedelta(1)

    return date_0,date_1


def fetch_prices(symbols,start_date,end_date):

    # get prices from yahoo finance
    names = ','.join(symbols)
    errors = 0
    message = []
    df = []
    try:
        yf.pdr_override()
        df = pdr.get_data_yahoo(
            symbols,
            start=start_date,
            end=end_date,
            group_by="ticker",
            progress=False,
        )
        if len(df) == 0:
            errors = -1
            message = 'Yahoo Finance query returned an empty dataset'
    except Exception as exception:
        errors = 1
        message = exception

    return df,errors,message


def modify_prices(df,tkids):

    # for more than one ticker
    if len(tkids) > 1:
        df = df.stack(level=[0])
        df.reset_index(inplace=True)
        df.rename(columns={'level_1':'symbol'}, inplace=True)
        df.dropna(inplace=True)

        # add ticker ids based on symbols
        df["ticker_id"] = df.apply(
            lambda row:get_ticker_id(row,tkids),
            axis=1
        )

        # drop symbol and retain only columns needed
        df.drop("symbol",axis=1,inplace=True)
    else:
        df.reset_index(inplace=True)
        df.dropna(inplace=True)
        tkid = tkids.values()
        df["ticker_id"] = tkid[0]

    # rename columns appropriately
    df.columns = map(str.lower, df.columns)
    df.columns = df.columns.str.replace(" ","_")
    return df


def upload_prices(df):

    # get database engine
    try:
        db_eng = db.get_engine()
    except:
        app = get_context()
        with app.app_context():
            db_eng = db.get_engine()

    # upload data
    df.to_sql(
        "prices",db_eng,if_exists="append",
        index=False,chunksize=10000
    )

def update_prices(full,tickers):

    # get dates
    start_date, end_date = get_dates(full)

    # fetch data
    symbols = [sym for _,sym in tickers]
    df,err,msg = fetch_prices(symbols,start_date,end_date)
    if err < 0 or err > 0:
        result = {"errors":err, "message": msg}
        return result


    tkids = {sym:tkid for tkid,sym in tickers}
    df = modify_prices(df,tkids)
    try:
        upload_prices(df)
        result = {"errors": 0, "message":[]}
    except Exception as exception:
        result = {"errors": 1, "message":exception}

    return result
