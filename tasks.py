# _*_ coding: utf-8 -*-

from flask import Flask
from celery.utils.log import get_task_logger

from run import celery as app
from utils import get_chunks, get_tickers, update_prices

import functools

logger = get_task_logger(__name__)


class EmptyDataFrameException(Exception):
    def __init__(self,message,errors):
        super(EmptyDataFrameException,self).__init__(message,errors)


class UpdateDabaseException(Exception):
    def __init__(self,message,errors):
        super(UpdateDabaseException,self).__init__(message,errors)


class EmptyTickersException(Exception):
    def __init__(self,message):
        super(UpdateDabaseException,self).__init__(message)


@app.task(bind=True)
def add_prices(self,full,tickers=None):

    if tickers is None:
        tickers =  get_tickers()

    try:
        if len(tickers) == 0 or tickers is None:
            result = {"errors":-1,"message":"No tickers provided"}
            raise EmptyTickersException(result["message"])

        result = update_prices(full,tickers)

        if result["errors"] < 0:
            raise  EmptyDataFrameException(
                "Empty data returned",
                result["message"]
            )

        elif result["errors"] > 0:
            raise  UpdateDabaseException(
                "Datase update failed",
                result["message"]
            )

    except (EmptyTickersException) as error:
        logger.warning(error)

    except (EmptyDataFrameException) as error:
        raise self.retry(exc=error, max_retries=5)

    except (UpdateDabaseException) as error:
        logger.error(error)

    else:
        typestr = "Full" if full else "Latest"
        symbols = [sym for _,sym in tickers]
        names = ','.join(symbols)
        msg = "{0} update for <{1}> tickers passed....".format(
            typestr,names
        )
        result["message"] = msg

    return result



@app.task
def add_ticker_prices(full,tickers=None):

    from celery import group
    if tickers is None:
        tickers =  get_tickers()

    nchunks = 10 if full else 50
    chunks = get_chunks(tickers,nchunks)
    job = group(
        add_prices.s(full,tickers=chunk) for chunk in chunks
    )
    result = job.apply_async()
