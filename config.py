# _*_ coding: utf-8 -*-

import os
from celery.schedules import crontab
from kombu import Exchange, Queue

from constants import UPDATE_TIME

import utils

# app config
APP_NAME = "trader"
VERSION = "v1"
URL_PREFIX = "/{0}/api/{1}".format(
    APP_NAME, VERSION
)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
JSON_SORT_KEYS = False
PROPAGATE_EXCEPTIONS = True


# jwt config
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access","refresh"]


# database configuration
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = utils.get_url("postgres")


# babel config
BABEL_DEFAULT_LOCALE = "en"
BABEL_DEFAULT_TIMEZONE = "est"


# celery config
BROKER_POOL_LIMIT = 1
BROKER_CONNECTION_TIMEOUT = 10

CELERY_BROKER_URL = utils.get_url("redis-broker")
CELERY_DEFAULT_QUEUE = "default"
CELERY_QUEUES = (
    Queue("default", Exchange("default"), routing_key="default"),
)

CELERY_IMPORTS = ("tasks")
CELERY_TIMEZONE = "EST"
CELERY_TRACK_STARTED = True
CELERY_SEND_EVENTS = True

CELERY_RESULT_BACKEND = utils.get_url("redis-backend")
CELERY_TASK_RESULT_EXPIRES = 60*5 # 5 minutes
CELERY_REDIS_MAX_CONNECTIONS = 10
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERYBEAT_SCHEDULE_FILENAME = "logs/beat.schedule"
CELERYBEAT_SCHEDULE = {
    "daily-update": {
        "task": "tasks.add_chunked_prices",
        "schedule": crontab(
            day_of_week=(2,3,4,5,6),
            hour=UPDATE_TIME.hour,
            minute=UPDATE_TIME.minute,
        ),
        "args":(False,),
        "kwargs": {"tickers": None},
    },
    "prune-expired-tokens": {
        "task": "tasks.prune_tokens",
        "schedule": crontab(minute=0,hour="*/1"),
        "args": (),
        "kwargs": {},
    }

}
