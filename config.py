# _*_ coding: utf-8 -*-

import os
from celery.schedules import crontab
from kombu import Exchange, Queue

from constants import UPDATE_TIME

# app config
VERSION = 'v1'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
JSON_SORT_KEYS = False

# database config
POSTGRES = {
    "user": "postgres",
    "pw": "password",
    "db": "shawshank",
    "host": "localhost",
    "port": "5432",
}

SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
#SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
SQLALCHEMY_DATABASE_URI = "postgresql://{user}:{pw}@{host}:{port}/{db}".format(
    **POSTGRES
)


# babel config
BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'est'


# celery config
BROKER_POOL_LIMIT = 1
BROKER_CONNECTION_TIMEOUT = 10

CELERY_BROKER_URL="amqp://localhost:5672"
CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
)
CELERY_IMPORTS = ('tasks')
CELERY_TIMEZONE = 'EST'

CELERY_RESULT_BACKEND="redis://localhost:6379/2"
CELERY_TASK_RESULT_EXPIRES = 60*60*24*28 # 28 days
CELERY_REDIS_MAX_CONNECTIONS = 1
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'weekday-latest-update': {
        'task': 'tasks.add_prices',
        'schedule': crontab(
            day_of_week="mon-fri",
            hour=str(UPDATE_TIME.hour),
            minute=str(UPDATE_TIME.minute),
        ),
        'args':(False,),
        'kwargs': {"tickers":None},
    }
}
