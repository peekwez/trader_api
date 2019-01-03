# _*_ coding: utf-8 -*-
from __future__ import absolute_import

import os

# app config
VERSION = 'v1'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# flask config
FLASK_ENV = "development"

# database config
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
