# _*_ coding: utf-8 -*-

from flask import Flask
from celery.utils.log import get_task_logger

from run import celery as app
from utils import (get_chunks, get_dates, update_logs,
                   get_tickers, update_prices, prune_expired_tokens)

logger = get_task_logger(__name__)

class ReturnedEmptyData(Exception):
    pass

class PricesUpdateFailed(Exception):
    pass

class PruneTokensFailed(Exception):
    pass

@app.task
def prune_tokens():
    try:
        prune_expired_tokens()
    except:
        raise PruneTokensFailed("Prune tokens database failed")
    return {"message": "Expired tokens deleted"}


@app.task(bind=True)
def add_prices(self,tickers,start_date,end_date):

    # try and catch error
    try:
        result = update_prices(tickers, start_date, end_date)

        if result["errors"] < 0:
            raise  ReturnedEmptyData(result["message"])

        elif result["errors"] > 0:
            raise  PricesUpdateFailed(result["message"])

    except (EmptyDataFrameException) as error:
        raise self.retry(exc=error, max_retries=5)

    except (UpdateDabaseException) as error:
        logger.error(error)

    else:
        symbols = [sym for _,sym in tickers]
        names = ','.join(symbols)
        msg = "{0} to {1} update for <{2}> tickers passed..".format(
            start_date,end_date,names
        )
        result["message"] = msg

    return result


@app.task(bind=True,ignore_result=True)
def add_chunked_prices(self,on_commit=False,tickers=None):

    from celery import group

    # get tickers if none provided
    if tickers is None:
        tickers =  get_tickers()

    # get start and end dates
    start_date, end_date = get_dates(on_commit)

    # chunk tickers in groups of 10 or 15
    nchunks = 10 if on_commit else 15
    chunks = get_chunks(tickers,nchunks)

    # group all jobs and submit to queue
    job = group(
        add_prices.s(
            chunk,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        ) for chunk in chunks
    )

    # run jobs
    result = job.apply_async()

    # add update date to logs only once()
    update_logs(end_date,self.request.id)
