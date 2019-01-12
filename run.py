# _*_ coding: utf-8 -*-

import warnings
warnings.simplefilter(action="ignore", category=Warning)

from flask import Flask
from flask_babel import Babel
from celery import Celery

from extensions import db, jwt
from models import TokenBlackList

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

    # initialize flask app
    app = Flask(__name__)
    app.config.from_object(config_file)

    # babel
    babel = Babel(app)

    # register api
    from app import trader
    app.register_blueprint(
        trader,
        url_prefix= app.config["URL_PREFIX"]
    )

    # initialize db
    db.init_app(app)

    # initialize jwt
    jwt.init_app(app)

    return app

# initialize app
app = create_app("config")

# initialize celery
celery = make_celery(app)

# revoked callback func
@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return TokenBlackList.is_revoked(decoded_token)

# start app
if __name__ == "__main__":
    app.run(debug=True)
