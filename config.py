# _*_ coding: utf-8 -*-

import os
from celery.schedules import crontab
from kombu import Exchange, Queue

from constants import UPDATE_TIME

# app config
APP_NAME = "trader"
VERSION = "v1"
URL_PREFIX = "/{0}/api/{1}".format(
    APP_NAME, VERSION
)

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
#CELERY_BROKER_URL="redis://localhost:6379"
CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
)

CELERY_IMPORTS = ('tasks')
CELERY_TIMEZONE = 'EST'
CELERY_TRACK_STARTED = True
CELERY_SEND_EVENTS = True

CELERY_RESULT_BACKEND="redis://localhost:6379/3"
CELERY_TASK_RESULT_EXPIRES = 60*5 # 5 minutes
CELERY_REDIS_MAX_CONNECTIONS = 10
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


CELERYBEAT_SCHEDULE = {
    'daily-update': {
        'task': 'tasks.add_chunked_prices',
        'schedule': crontab(
            day_of_week=(2,3,4,5,6),
            hour=UPDATE_TIME.hour,
            minute=UPDATE_TIME.minute,
        ),
        'args':(False,),
        'kwargs': {"tickers":None},
    }
}
