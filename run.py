# _*_ coding: utf-8 -*-
from __future__ import absolute_import

from flask import Flask

def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    vers = app.config['VERSION']

    from app import trader
    app.register_blueprint(
        trader,
        url_prefix='/api/{0}'.format(vers)
        )

    from model import db
    db.init_app(app)

    return app


if __name__ == "__main__":
    app = create_app("config")
    app.run(debug=True)
