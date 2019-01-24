# _*_ coding: utf-8 -*-

from flask import Blueprint
from flask_restful import Api
from resources.home import Home
from resources.ticker import TickerResource
from resources.price import PriceResource
from resources import user

data = Blueprint('data',__name__)
api = Api(data)

api.add_resource(Home,'/info')

# user and authentication resources
api.add_resource(user.UserRegister,"/register")
api.add_resource(user.UserLogin,"/login")
api.add_resource(user.UserLogoutAcess,"/logout/access")
api.add_resource(user.UserLogoutRefresh,"/logout/refresh")
api.add_resource(user.TokenRefresh,"/token/refresh")
api.add_resource(user.UserResource,"/users","/users")
api.add_resource(user.SecretResource,"/secret")

# prices and ticker resources
api.add_resource(TickerResource,'/tickers')
api.add_resource(PriceResource,'/prices')
