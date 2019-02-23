# _*_ coding: utf-8 -*-

import warnings
warnings.simplefilter(action="ignore", category=Warning)

from click import progressbar
from logbook import Logger
import pandas as pd
import numpy as np

from zipline.utils.cli import maybe_show_progress
from zipline.data.bundles import core as bundles

log = Logger(__name__)

def get_symbols(market):
    filename = "_tmp_data/symbols_{0}.csv".format(market)
    df = pd.read_csv(filename)
    symbols = df["symbol"].values
    return symbols

def get_prices(market):
    filename = "_tmp_data/prices_{0}.csv".format(market)
    df = pd.read_csv(
        filename,
        parse_dates=["date"],
        index_col=None,
        memory_map=True
    )
    return df

def fetch_data_table(symbol, data):
    """ Load data table from trader database.
    """

    # filter data in memory by column
    df = data.loc[data["symbol"] == symbol]
    df.drop(columns=["symbol"], inplace=True)

    # drop duplicate dates
    df.drop_duplicates(subset=["date"],keep="first",inplace=True)

    # use date as index
    df.set_index("date",inplace=True)
    return df

def _pricing_iter(symbols, data, metadata,calendar,show_progress):
    with maybe_show_progress(symbols,show_progress,
                             label="Loading Shawshank pricing data: ") as it:

        for sid,symbol in enumerate(it):

            # get data frame
            df = fetch_data_table(symbol,data)

            # write metadata
            start_date = df.index[0]
            end_date = df.index[-1]

            ac_date = end_date + pd.Timedelta(days=1)
            metadata.iloc[sid] = start_date, end_date, ac_date, symbol

            # check if all session are in there
            sessions = calendar.sessions_in_range(start_date, end_date)
            df = df.reindex(
                sessions.tz_localize(None)
            ).fillna(0.0)

            yield sid, df

def trader_equities(market):
    def ingest(environ,
               asset_db_writer,
               minute_bar_writer,
               daily_bar_writer,
               adjustment_writer,
               calendar,
               start_session,
               end_session,
               cache,
               show_progress,
               output_dir):

        symbols = get_symbols(market)
        data = get_prices(market)

        dtype = [
            ("start_date", "datetime64[ns]"),
            ("end_date","datetime64[ns]"),
            ("auto_close_date","datetime64[ns]"),
            ("symbol","object")
        ]
        metadata = pd.DataFrame(np.empty(len(symbols), dtype=dtype))

        daily_bar_writer.write(
            _pricing_iter(symbols, data, metadata, calendar, show_progress),
            show_progress=show_progress
        )
        metadata["exchange"] ="TRADER-%s"%market

        asset_db_writer.write(equities=metadata)
        adjustment_writer.write()

    return ingest
