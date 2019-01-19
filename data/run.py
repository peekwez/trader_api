# _*_ coding: utf-8 -*-

import warnings
warnings.simplefilter(action="ignore", category=Warning)

from flask import Flask
from flask_babel import Babel
from celery import Celery

from extensions import db, jwt
from models import TokenBlackList
from utils import get_env, get_test_config


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



def create_app():

    # initialize flask app
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=get_env("SECRET_KEY"),
        JWT_SECRET_KEY=get_env("JWT_SECRET_KEY")
    )
    app.config.from_pyfile("config.py",silent=True)

    # check if testing mode
    test_config = get_test_config()
    if test_config:
        app.config.update(test_config)


    # register api
    from app import data
    app.register_blueprint(
        data,
        url_prefix= app.config["URL_PREFIX"]
    )

    # initialize babel
    babel = Babel(app)

    # initialize db
    db.init_app(app)

    # initialize jwt
    jwt.init_app(app)

    return app

# initialize app
app = create_app()

# initialize celery
celery = make_celery(app)

# revoked callback func
@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return TokenBlackList.is_revoked(decoded_token)


# start app
if __name__ == "__main__":
    app.run(debug=True)
