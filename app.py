# _*_ coding: utf-8 -*-

from flask import Blueprint
from flask_restful import Api
from resources.home import Home
from resources.ticker import TickerResource
from resources.price import PriceResource

trader = Blueprint('trader',__name__)
api = Api(trader)


# route
api.add_resource(Home,'/')
api.add_resource(TickerResource,'/tickers')
api.add_resource(PriceResource,'/prices')
