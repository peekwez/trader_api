# _*_ coding: utf-8 -*-

from flask import Flask
from marshmallow import fields, post_dump, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy, models_committed
from sqlalchemy import event
from flask_babel import lazy_gettext as _
from datetime import datetime
from sqlalchemy_utils import ChoiceType

from itertools import groupby

ma = Marshmallow()
db = SQLAlchemy()

class Ticker(db.Model):

    MARKETS = (
        (u"CA",_(u"Canada")),
        (u"US",_(u"United States")),
    )

    TYPES = (
        (u"security",_(u"Security")),
        (u"index",_(u"Index")),
    )


    __tablename__ = "tickers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250), nullable=False)
    symbol = db.Column(db.String(50), unique=True, nullable=False)
    sector = db.Column(db.String(250), nullable=True)
    industry = db.Column(db.String(250), nullable=True)
    exchange = db.Column(db.String(50),nullable=True)
    market = db.Column(
        ChoiceType(MARKETS),
        nullable=False
    )
    type = db.Column(
        ChoiceType(TYPES),
        nullable=False
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        onupdate=datetime.utcnow,
    )

    def __repr__(self):
        return '<Ticker: {0} - {1}>'.format(self.name,self.symbol)

    def __commit_insert__(self):
        return (self.id,self.symbol)


class Price(db.Model):

    __tablename__ = "prices"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticker = db.relationship(
        'Ticker',
        backref=db.backref('prices',order_by='Ticker.symbol',lazy='dynamic'),
    )
    ticker_id = db.Column(
        db.Integer,
        db.ForeignKey('tickers.id',ondelete='CASCADE'),
        nullable=False
    )
    date = db.Column(db.Date,nullable=False)
    open = db.Column(db.Float, nullable=False)
    low  =  db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    adj_close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Price: {0} - OHLC>'.format(self.ticker.symbol)


class TickerPrices(object):
    def __init__(self,ticker,prices):
        self.ticker = ticker
        self.prices = prices


class TickerPricesFactory:

    @staticmethod
    def create_objects(prices):
        keyfun = lambda p: p.ticker_id
        objs = []
        for k,g in groupby(prices,key=keyfun):
            tkprices = list(g)
            ticker  = tkprices[0].ticker
            objs.append(TickerPrices(ticker,tkprices))
        return objs


class TickerSchema(ma.Schema):

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(1))
    symbol = fields.String(required=True, validate=validate.Length(1))
    sector = fields.String(validate=validate.Length(1), allow_none=True)
    industry = fields.String(validate=validate.Length(1), allow_none=True)
    exchange = fields.String(validate=validate.Length(1), allow_none=True)
    market = fields.String(required=True, validate=validate.Length(1))
    type = fields.String(required=True, validate=validate.Length(1))

    class Meta:
        fields = (
            "name", "exchange","symbol", "type",
            "market","sector","industry",
        )
        ordered = True


class PriceSchema(ma.Schema):

    class Meta:
        fields  = (
            "date","open","high",
            "low","close","adj_close",
            "volume"
        )
        ordered =  True


class TickerPricesSchema(ma.Schema):

    ticker = fields.Nested(TickerSchema)
    prices = fields.Nested(PriceSchema,many=True)

    class Meta:
        ordered = True
