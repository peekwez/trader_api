# _*_ coding: utf-8 -*-

from flask import Flask
from flask_babel import lazy_gettext as _
from sqlalchemy_utils import ChoiceType, EmailType
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import decode_token

from extensions import db
from itertools import groupby
from datetime import datetime

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
    market = db.Column(ChoiceType(MARKETS),nullable=False)
    type = db.Column(ChoiceType(TYPES),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now,nullable=False)
    updated_at = db.Column(db.DateTime,onupdate=datetime.now)


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


# price update logs model
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


# user model
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name  = db.Column(db.String(120), nullable=False)
    email      = db.Column(EmailType(250), unique=True, nullable=False)
    password   = db.Column(db.String(120), nullable=False)
    is_admin   = db.Column(db.Boolean, nullable=False, default=False)
    last_login = db.Column(db.DateTime,default=datetime.now,nullable=False)
    date_joined = db.Column(db.DateTime,default=datetime.now,nullable=False)


    def __repr__(self):
        obj_name = "Admin" if self.is_admin else "User"
        return '<{0}: {1} {2}>'.format(
            obj_name,
            self.first_name,
            self.last_name
        )

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_last_login(self):
        self.last_login = datetime.now()
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


    @classmethod
    def get_all_users(cls):
        return cls.query.order_by(
            cls.last_name.asc(),
            cls.first_name.asc()
        ).all()

    @classmethod
    def delete_users(cls,ids):
        users = cls.query.filter(cls.id.in_(ids))
        for user in users:
            db.session.delete(user)
        db.session.commit()



class NoResultFound(Exception):
    pass

def _epoch_utc_to_datetime(epoch_utc):
    return datetime.fromtimestamp(epoch_utc)

class TokenBlackList(db.Model):

    __tablename__ = "token_black_list"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    token_type = db.Column(db.String(10), nullable=False)
    revoked = db.Column(db.Boolean, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)

    @classmethod
    def add_token(cls, encoded_token):
        decoded_token = decode_token(encoded_token)
        params = dict(
            jti = decoded_token["jti"],
            token_type = decoded_token["type"],
            expires = _epoch_utc_to_datetime(
                decoded_token["exp"]
            ),
            revoked = False
        )

        token = cls(**params)
        db.session.add(token)
        db.session.commit()

    @classmethod
    def is_revoked(cls, decoded_token):
        jti = decoded_token["jti"]
        try:
            token = cls.query.filter_by(jti=jti).one()
            return token.revoked
        except NoResultFound:
            return True


    @classmethod
    def revoke_token(cls, jti):
        try:
            token = cls.query.filter_by(jti=jti).one()
            token.revoked = True
            db.session.commit()
        except NoResultFound:
            raise TokenNotFound("Could not find the token {0}".format(token_id))
