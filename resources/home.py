# _*_ coding: utf-8 -*-

from flask import current_app
from flask_restful import Resource


class Home(Resource):
    def get(self):
        vers = current_app.config['VERSION']
        return {"api": "trader", "version":vers}