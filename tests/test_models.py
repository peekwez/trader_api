#_*_ coding: utf-8 -*-

import sqlite3

import pytest
import extensions as ext


def test_user(user):
    assert not user.is_admin

def test_admin(admin):
    assert admin.is_admin

def test_tickers(tickers):
    pass
