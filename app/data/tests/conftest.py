#_*_ coding: utf-8 -*-

import os

import pytest

from extensions import db, ma, jwt
from factories import UserFactory, AdminFactory, TickerFactory
from constants import TMP_FD, TMP_PATH

@pytest.fixture(scope="session")
def app():
    from run import app
    yield app
    os.close(TMP_FD)
    os.unlink(TMP_PATH)


@pytest.fixture(scope="session")
def admin(app):
    with app.app_context():
        admin = AdminFactory()
    yield admin


@pytest.fixture(scope="session")
def user(app):
    with app.app_context():
        user = UserFactory()
    yield user


@pytest.fixture(scope="session")
def tickers(app):
    with app.app_context():
        tickers = [TickerFactory() for _ in range(50)]
    yield tickers
