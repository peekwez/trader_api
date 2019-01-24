# _*_ coding: utf-8 -*-

import os
import sys

from sqlalchemy import func, and_
from extensions import db

from models import Price, Ticker, UpdatesLog, TokenBlackList
from constants import (OPERATORS, PRICE_COLUMNS,
                       TICKER_COLUMNS, UPDATE_TIME,
                       TMP_PATH, AGGREGATORS)

from pandas_datareader import data as pdr
from datetime import datetime, timedelta
import fix_yahoo_finance as yf


class ImproperlyConfigured(Exception):
    pass

date_fmt = lambda x: datetime.strptime(x,'%Y-%m-%d')

def add_price_params(parser):

    # suffix for numerical and date queries
    operators = OPERATORS

    # add ticker symbol
    parser.add_argument("symbol", type=str)

    # add date parser
    for ops in operators:
        parser.add_argument("date{0}".format(ops), type=date_fmt)

    # add OHCL parser
    fields = ("open","low","high","close","adj_close","volume","dollar_volume")
    for field in fields:
        for ops in operators:
            parser.add_argument("{0}{1}".format(field,ops), type=float)

    return parser


def add_ticker_params(parser):

    # base params
    fields = ("symbol","sector","industry","exchange","market","type")
    for field in fields:
        parser.add_argument("{0}".format(field),type=str)

    # add price params
    parser = add_price_params(parser)

    # aggregate price params
    aggregators = AGGREGATORS
    operators = OPERATORS
    fields = ("open","low","high","close","adj_close","volume","dollar_volume")
    for agg in aggregators:
        for field in fields:
            for ops in operators:
                parser.add_argument("{0}{1}{2}".format(agg,field,ops),type=float)

    return parser

def comp(a,b,ops):

    # interface for sql operators for filtering
    if ops == "gte":
        return a >= b
    elif ops == "gt":
        return a > b
    elif ops == "lte":
        return a <= b
    elif ops == "lt":
        return a < b
    elif ops == "eq":
        return a == b


def agg_comp(agg):

    # interface for sql aggregator functions
    if agg == "avg":
        return func.avg
    elif agg == "min":
        return func.min
    elif agg == "max":
        return func.max


def get_ticker_filters(args):

    # get filter for tickers
    columns = TICKER_COLUMNS
    columns.update(PRICE_COLUMNS)
    base_bool = ()
    price_bool = ()
    price_agg = ()
    for key in args.keys():
        if args.get(key) is not None:
            if '__' in key:
                value = args.get(key)
                try:
                    agg, param, ops = key.split("__")
                    aggfun = agg_comp(agg)
                    column = aggfun(columns[param])
                    price_agg += comp(column,value,ops),
                except ValueError:
                    param, ops = key.split("__")
                    column = columns[param]
                    price_bool += comp(column,value,ops),
            else:
                value = args.get(key).split(",")
                base_bool += columns[key](value),

    if price_agg and len(price_agg) > 1:
        price_agg = (and_(*price_agg))

    return base_bool, price_bool, price_agg


def get_price_filters(args):

    bools = ()
    # get symbol ids
    if args.has_key("symbol"):
        symbol = args.get('symbol').split(',')
        ticker_id = Ticker.query.with_entities(
            Ticker.id
        ).filter(Ticker.symbol.in_(symbol))


        # build boolean for query
        bools += Price.ticker_id.in_(ticker_id),


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


def get_context(func):
    def wrapper(*args,**kwargs):
        from trader import app
        with app.app_context():
            return func(*args,**kwargs)
    return wrapper


def get_chunks(l,n):

    # chunk data for downloads
    for k in range(0,len(l),n):
        yield l[k:k+n]


def get_ticker_id(row,tkids):

    # get ticker id based on symbol
    key = row['symbol']
    return tkids[key]


@get_context
def get_tickers():
    tickers = Ticker.get_all_tickers()
    tickers = [(tk.id,tk.symbol) for tk in tickers]
    return tickers


@get_context
def update_logs(end_date,task_id):
    UpdatesLog.update_log(end_date,task_id)

@get_context
def get_dates(on_commit=False):

    # date 1 date log
    date_1 = datetime.now() - timedelta(1)
    if date_1.time() < UPDATE_TIME:
        date_1 = date_1 - timedelta(1)
    date_1 = date_1.replace(hour=0,minute=0,second=0,microsecond=0)


    # check last update
    if on_commit:

        # check for start date for commit updates
        log = UpdatesLog.query.order_by("date asc").limit(1).first()

        if log:
            date_0 = log.date

            # check for the latest update
            log = UpdatesLog.query.order_by("date desc").limit(1).first()
            if log.date > date_0:
                date_1 = log.date

        else:
            year = datetime.now().year-15;
            date = datetime(year,1,1)

            log = UpdatesLog(date=date,task_id="<initial_update_0000>")
            db.session.add(log)
            db.session.commit()

            date_0 = log.date # start date
    else:
        log = UpdatesLog.query.order_by("date desc").limit(1).first()
        date_0 = log.date + timedelta(1)

    return date_0,date_1


def fetch_prices(symbols,start_date,end_date):

    # get prices from yahoo finance
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


@get_context
def upload_prices(df):

    # get database engine
    db_eng = db.get_engine()

    # upload data
    df.to_sql(
        "prices",db_eng,if_exists="append",
        index=False,chunksize=10000
    )


def update_prices(tickers, start_date, end_date):

    # fetch date
    symbols = [sym for _,sym in tickers]
    df,err,msg = fetch_prices(symbols,start_date,end_date)
    if err < 0 or err > 0:
        result = {"errors":err, "message": msg}
        return result

    # get prices if no errors
    tkids = {sym:tkid for tkid,sym in tickers}
    df = modify_prices(df,tkids)

    try:
        upload_prices(df)
        result = {"errors": 0, "message":[]}
    except Exception as exception:
        result = {"errors": 1, "message":exception}

    return result


def get_env(var_name):

    # get environment variable
    try:
        return os.environ[var_name]
    except KeyError:
        error_message = "Set the {0} environment variable".format(var_name)
        raise ImproperlyConfigured(error_message)


def get_url(service):

    # get address for services supporting app
    if service is "rabbit":
        params = dict(
            user=get_env("RABBIT_USER"),
            password=get_env("RABBIT_PASS"),
            host=get_env("RABBIT_HOST"),
            port=get_env("RABBIT_PORT"),
            vhost=get_env("RABBIT_VHOST")
        )
        url="amqp://{user}:{password}@{host}:{port}/{vhost}".format(**params)

    elif service is "postgres":
        params = dict(
            user=get_env("POSTGRES_USER"),
            password=get_env("POSTGRES_PASS"),
            db=get_env("POSTGRES_DB"),
            host=get_env("POSTGRES_HOST"),
            port=get_env("POSTGRES_PORT")
        )
        url="postgresql://{user}:{password}@{host}:{port}/{db}".format(**params)

    elif service is "redis":
        params = dict(
            host=get_env("REDIS_HOST"),
            port=get_env("REDIS_PORT"),
            db=get_env("REDIS_DB"),
        )
        url="redis://{host}:{port}/{db}".format(**params)

    elif service is "memcached":
        params = dict(
            host=get_env("MEMCACHED_HOST"),
            port=get_env("MEMCACHED_PORT")
        )
        url="postgresql://{host}:{port}".format(**params)
    elif service is "testing":
        params = dict(db_path=TMP_PATH)
        url="sqlite:///{db_path}".format(**params)

    return url

def get_test_config():

    # get config for testing
    test_config = {}
    if "pytest" in sys.modules:
        test_config = {
            "TESTING": True,
            "DATABASE": TMP_PATH,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "SQLALCHEMY_DATABASE_URI":get_url("testing")
        }
    return test_config


@get_context
def prune_expired_tokens():
    
    # remove expired tokens
    now = datetime.now()
    expired = TokenBlackList.query.filter(
        TokenBlackList.expires < now
    ).all()
    if expired:
        for token in expired:
            db.session.delete(token)
