# _*_ coding: utf-8 -*-

from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from models import Price
from serializers import TickerPricesSchema
from utils import add_price_params, get_price_filters

prices_schema = TickerPricesSchema(many=True)

parser = reqparse.RequestParser()
parser = add_price_params(parser)

class PriceResource(Resource):

    @jwt_required
    def get(self):
        args = parser.parse_args(strict=True)
        if not any(args.values()):
            return {"message":"At least one argument required"},401
        filters = get_price_filters(args)

        ticker_prices = Price.filter_ticker_prices(filters)
        data = prices_schema.dump(ticker_prices).data

        return {'data':data},200
