# _*_ coding: utf-8 -*-

import warnings
warnings.simplefilter(action="ignore", category=Warning)
from flask import Flask
from flask_babel import Babel
from celery import Celery
from flask_sqlalchemy import models_committed
from models import Ticker

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True
        def __call__(self,*args,**kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


def create_app(config_file):

    app = Flask(__name__)
    app.config.from_object(config_file)

    babel = Babel(app)

    from app import trader
    vers = app.config['VERSION']
    app.register_blueprint(
        trader,
        url_prefix='/trader/api/{0}'.format(vers)
    )

    from models import db
    db.init_app(app)

    app.config['JSON_SORT_KEYS'] = False
    return app

app = create_app("config")
celery = make_celery(app)


@models_committed.connect_via(app)
def on_models_committed(sender, changes):
    tickers = []
    for model, change in changes:
        if isinstance(model,Ticker):
            if hasattr(model,'__commit_insert__') and change == "insert":
                ticker = model.__commit_insert__()
                tickers.append(ticker)

    if tickers:
        from tasks import add_full_prices
        add_full_prices(True,tickers)

if __name__ == "__main__":
    app.run(debug=True)
