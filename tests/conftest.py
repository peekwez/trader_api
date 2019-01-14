#_*_ coding: utf-8 -*-

import os
import tempfile

import pytest
import random

from run import create_app
from extensions import db, ma, jwt
from factories import UserFactory, AdminFactory, TickerFactory


@pytest.fixture
def app():
    db_fd, db_path  = tempfile.mkstemp()
    app = create_app({
        "TESTING": True,
        "DATABASE": db_path,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    yield app

    os.close(db_fd)
    os.unlink(app.config["DATABASE"])


@pytest.fixture
def admin(app):
    with app.app_context():
        admin = AdminFactory()
    yield admin


@pytest.fixture
def user(app):
    with app.app_context():
        user = UserFactory()
    yield user


@pytest.fixture
def tickers(app):
    with app.app_context():
        tickers = [TickerFactory() for _ in range(50)]
    yield tickers
