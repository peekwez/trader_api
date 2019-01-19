# _*_ coding: utf-8 -*-

from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

from functools import wraps

ma  = Marshmallow()
db  = SQLAlchemy()
jwt = JWTManager()
