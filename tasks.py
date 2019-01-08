# _*_ coding: utf-8 -*-

from flask import Flask
from celery.utils.log import get_task_logger

from run import celery as app
from utils import get_chunks, get_tickers, update_prices

import functools

logger = get_task_logger(__name__)


class EmptyDataFrameException(Exception):
    def __init__(self,message,errors):
        super(EmptyDataFrameException,self).__init__(message)


class UpdateDabaseException(Exception):
    def __init__(self,message,errors):
        super(UpdateDabaseException,self).__init__(message)


class EmptyTickersException(Exception):
    def __init__(self,message,errors):
        super(UpdateDabaseException,self).__init__(message)


@app.task(bind=True)
def add_prices(self,full,tickers=None):

    if tickers is None:
        tickers =  get_tickers()

    try:
        if len(tickers) == 0 or tickers is None:
            result = {"errors":-1,"message":"No tickers to update"}
            raise EmptyTickersException(result["message"])

        result = update_prices(full,tickers)

        if result["errors"] < 0:
            raise  EmptyDataFrameException(result["message"])

        elif result["errors"] > 0:
            raise  UpdateDabaseException(result["message"])

    except (EmptyTickersException) as error:
        logger.warning(error)

    except (EmptyDataFrameException) as error:
        raise self.retry(exc=error, max_retries=5)

    except (UpdateDabaseException) as error:
        logger.error(error)

    else:
        typestr = "Full" if full else "Latest"
        symbols = [sym for _,sym in tickers]
        names = ','.join(symbols) if full else "_ALL_"
        logger.info("{0} update for <{1}> tickers passed....".format(typestr,names))

    return result


def add_full_prices(full,tickers=None):

    from celery import group
    if tickers is None:
        tickers =  get_tickers()

    chunks = get_chunks(tickers,10)
    job = group(
        add_prices.s(full,tickers=chunk) for chunk in chunks
    )
    result = job.apply_async()
