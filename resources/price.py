# _*_ coding: utf-8 -*-

from flask import request
from flask_restful import Resource, reqparse
from models import db, Price, TickerPricesSchema#, TickerPricesFactory
from utils import add_price_params, get_price_filters

prices_schema = TickerPricesSchema(many=True)

parser = reqparse.RequestParser()
parser = add_price_params(parser)

class PriceResource(Resource):

    def get(self):
        args = parser.parse_args(strict=True)
        filters = get_price_filters(args)

        ticker_prices = Price.filter_ticker_prices(filters)
        data = prices_schema.dump(ticker_prices).data

        return {'status':'success','data':data},200
