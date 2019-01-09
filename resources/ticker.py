# _*_ coding: utf-8 -*-

from flask import request
from flask_restful import Resource, reqparse
from models import db, Ticker, TickerSchema
from utils import get_ticker_filters
from sqlalchemy import tuple_

tickers_schema = TickerSchema(many=True)
ticker_schema = TickerSchema()

parser = reqparse.RequestParser()
parser = parser.add_argument("symbol",type=str)
parser = parser.add_argument("sector",type=str)
parser = parser.add_argument("industry",type=str)
parser = parser.add_argument("exchange",type=str)
parser = parser.add_argument("market",type=str)
parser = parser.add_argument("type",type=str)

class TickerResource(Resource):

    def get(self):
        args = parser.parse_args(request,strict=True)
        if len(args) > 0:
            filters = get_ticker_filters(args)
            tickers = Ticker.query.order_by(Ticker.id.asc()).filter(*filters)
        else:
            tickers = Ticker.query.order_by(Ticker.id.asc()).all()
        tickers = tickers_schema.dump(tickers).data
        return {'status':'success','data':tickers},200


    def post(self):
        json_data = request.get_json(force=True)
        if not json_data:
            return {'message': 'No input data provided'},400

        # validate and deserialize input
        data, errors = tickers_schema.load(json_data)
        if errors:
            return errors,422

        # check if any of tickers already exists
        items = [(item["symbol"],) for item in data]
        tickers = Ticker.query.filter(Ticker.symbol.in_(items)).all()


        # if any of the tickers exist don't pass; all or nothing
        if tickers:
            tmp = [ticker.symbol  for ticker in tickers]
            names = ",".join(tmp)
            return {'message': 'Ticker symbols %s already exists'%names},400

        # instantiate ticker and save
        tickers = [Ticker(**item) for item in data]

        # add tickers and commit
        db.session.add_all(tickers)
        db.session.commit()

        # return results
        result = tickers_schema.dump(tickers).data

        return {'status':'success', 'data':result},201


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
        ticker = Ticker.query.filter_by(symbol=symbol)


        # check if ticker exists
        if not ticker:
            return {'message': 'Ticker does not exist'},400

        ticker.update(data)
        db.session.commit()

        result = ticker_schema.dump(ticker).data

        return {"status": 'success', 'data': result},204


    def delete(self):
        args = parser.parse_args(request,strict=True)
        if not args.has_key("symbol"):
            return {'message': 'Symbol to delete is required'},400

        symbols = args.get("symbol").split(",")
        tickers = Ticker.query.filter(
            Ticker.symbol.in_(symbols)
        ).delete(synchronize_session=False)
        db.session.commit()

        return {"status": 'success'}, 204
