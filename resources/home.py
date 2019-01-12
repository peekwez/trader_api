# _*_ coding: utf-8 -*-

from flask import current_app
from flask_restful import Resource

import subprocess

class Home(Resource):
    def get(self):
        app_name = current_app.config["APP_NAME"]
        version = current_app.config['VERSION']
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"]
        ).decode("ascii").strip()
        return {"api": app_name, "version":version, "commit":commit}
