# _*_ coding: utf-8 -*-

from flask import Flask
from marshmallow import fields, post_dump, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_babel import lazy_gettext as _
from sqlalchemy_utils import ChoiceType, EmailType
from passlib.hash import pbkdf2_sha256 as sha256

from itertools import groupby
from datetime import datetime

ma = Marshmallow()
db = SQLAlchemy()

# schema models
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


    def update_ticker(self,data):
        for key, value in data.items():
            setattr(self,key,value)
        db.session.commit()

    @classmethod
    def filter_tickers(cls,filters):
        return cls.query.order_by(cls.id.asc()).filter(*filters).all()

    @classmethod
    def get_all_tickers(cls):
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def filter_by_kwargs(cls,**kwargs):
        return cls.query.filter_by(**kwargs).all()

    @classmethod # only admin
    def delete_tickers(cls,symbols):
        cls.query.filter(cls.symbol.in_(symbols)).delete(
            synchronize_session=False
        )
        db.session.commit()

    @classmethod # only admin
    def add_tickers(cls,data):
        tickers = [cls(**item) for item in data]
        db.session.add_all(tickers)
        db.session.commit()
        return tickers


    def __repr__(self):
        return '<Ticker: {0} - {1}>'.format(self.name,self.symbol)


# a model to attach prices to a single ticker
class TickerPrices(object):
    def __init__(self,ticker,prices):
        self.ticker = ticker
        self.prices = prices


# price model
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


    @classmethod
    def filter_prices(cls,filters):
        prices = cls.query.order_by(
            cls.ticker_id.asc(),
            cls.date.asc(),
        ).filter(*filters).all()
        return prices


    @classmethod
    def filter_ticker_prices(cls,filters):
        prices = cls.filter_prices(filters)
        keyfun = lambda p: p.ticker_id
        objs = []
        for k,g in groupby(prices,key=keyfun):
            tkprices = list(g)
            ticker  = tkprices[0].ticker
            objs.append(TickerPrices(ticker,tkprices))
        return objs

    def __repr__(self):
        return '<Price: {0} - OHLC>'.format(self.ticker.symbol)


class UpdatesLog(db.Model):
    __tablename__ = "updates_log"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime,unique=True,nullable=False)
    task_id = db.Column(db.String(250), nullable=True)

    @classmethod
    def update_log(cls,date,task_id):
        log = cls.query.filter_by(date=date).first()
        if not log:
            log = cls(date=date,task_id=task_id)
            db.session.add(log)
            db.session.commit()


class User(db.Model):
    __tablename = "users"

    id = db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name  = db.Column(db.String(120), nullable=False)
    email      = db.Column(EmailType(250), unique=True, nullable=False)
    password   = db.Column(db.String(120), nullable=False)
    is_admin   = db.Column(db.Boolean, nullable=False, default=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password,hash):
        return sha256.verify(password,hash)

    @classmethod
    def create_user(cls,data):
        user = cls(first_name=data["first_name"],
                   last_name=data["last_name"],
                   email=data["email"],
                   password=cls.generate_hash(data["password"])
               )
        return user

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()


    @classmethod # only admin
    def get_all_users(cls):
        return cls.query.order_by(
            cls.last_name.asc(),
            cls.first_name.asc()
        ).all()

    @classmethod # only admin
    def delete_users(cls,id):
        cls.query.filter(cls.id == id).delete()
        db.session.commit()


# schema serializers
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


class UserSchema(ma.Schema):

    class Meta:
        fields = (
            "first_name", "last_name",
            "email","is_admin", "id",
        )
        ordered = True
