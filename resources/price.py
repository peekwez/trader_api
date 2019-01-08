# _*_ coding: utf-8 -*-

from flask import request
from flask_restful import Resource, reqparse
from models import db, Price, TickerPricesSchema, TickerPricesFactory
from utils import add_price_params, get_price_filters

prices_schema = TickerPricesSchema(many=True)

parser = reqparse.RequestParser()
parser = add_price_params(parser)

class PriceResource(Resource):

    def get(self):
        args = parser.parse_args(strict=True)
        filters = get_price_filters(args)
        prices = Price.query.order_by(
            Price.ticker_id.asc(),
            Price.date.asc(),
        ).filter(*filters).all()
        ticker_prices = TickerPricesFactory.create_objects(
            prices
        )
        data = prices_schema.dump(ticker_prices).data
        return {'status':'success','data':data},200
