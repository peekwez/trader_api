# _*_ coding: utf-8 -*-
from __future__ import absolute_import

from flask import Blueprint
from flask_restful import Api
from resources.home import Home

trader = Blueprint('trader',__name__)
api = Api(trader)


# route
api.add_resource(Home,'/')
