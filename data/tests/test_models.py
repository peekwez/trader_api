#_*_ coding: utf-8 -*-

import sqlite3

import pytest
import utils
from extensions import db

def test_user(user,app):
    assert not user.is_admin

def test_admin(admin):
    assert admin.is_admin

def test_tickers(tickers):
    assert len(tickers) > 0
