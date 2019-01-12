# _*_ coding: utf-8 -*-

from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from models import Ticker
from serializers import TickerSchema
from utils import get_ticker_filters
from signals import after_post_tickers
from resources.user import admin_rights_required

tickers_schema = TickerSchema(many=True)
ticker_schema = TickerSchema()

parser = reqparse.RequestParser()
parser.add_argument("symbol",type=str)
parser.add_argument("sector",type=str)
parser.add_argument("industry",type=str)
parser.add_argument("exchange",type=str)
parser.add_argument("market",type=str)
parser.add_argument("type",type=str)

class TickerResource(Resource):

    @jwt_required
    def get(self):
        args = parser.parse_args(request,strict=True)
        if len(args) > 0:
            filters = get_ticker_filters(args)
            tickers = Ticker.filter_tickers(filters)
        else:
            tickers = Ticker.get_all_tickers()
        tickers = tickers_schema.dump(tickers).data
        return {'status':'success','data':tickers},200

    @admin_rights_required
    @jwt_required
    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'},400

        # validate and deserialize input
        data, errors = tickers_schema.load(json_data)
        if errors:
            return errors,422

        # check if any of tickers already exists
        items = [item["symbol"] for item in data]
        filters = (Ticker.symbol.in_(items),)
        tickers = Ticker.filter_tickers(filters)


        # if any of the tickers exist don't pass; all or nothing
        if tickers:
            tmp = [ticker.symbol  for ticker in tickers]
            names = ",".join(tmp)
            return {'message': 'Ticker symbols %s already exists'%names},400

        # instantiate ticker and save
        tickers = Ticker.add_tickers(data)

        # emit signal
        after_post_tickers.send(self,tickers=tickers)

        return {"message": "Tickers added to database"},201

    @admin_rights_required
    @jwt_required
    def put(self):
        args = parser.parse_args(request,strict=True)
        if not args.has_key("symbol"):
            return {'message': 'Symbol to update is required'},400

        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'},400

        # validate and deserialize input
        data, errors = ticker_schema.load(json_data,partial=True)
        if errors:
            return errors, 422
        symbol = args.get("symbol")
        ticker = Ticker.filter_by_kwargs(symbol=symbol)[0]


        # check if ticker exists
        if not ticker:
            return {'message': 'Ticker does not exist'},400

        ticker.update_ticker(data)

        return {"message": "Ticker {0} updated"},204


    @admin_rights_required
    @jwt_required
    def delete(self):
        args = parser.parse_args(request,strict=True)
        if not args.has_key("symbol"):
            return {'message': 'Symbol to delete is required'},400

        symbols = args.get("symbol").split(",")
        Ticker.delete_tickers(symbols)

        names = args.get("symbol")
        return {"message": 'Ticker <{0}> deleted'.format(names)}, 204
