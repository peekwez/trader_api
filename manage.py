# _*_ coding: utf-8 -*-
import warnings
warnings.simplefilter(action="ignore", category=Warning)

from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

from run import app
from models import db, Ticker, Price, UpdatesLog
from tasks import add_prices, add_chunked_prices
from constants import BANNER
import utils

manager = Manager(app)
shell = Shell(use_ipython=True)
server = Server(host="localhost",port=5000)
migrate = Migrate(app, db)

@manager.shell
def _make_context():
    kwargs = dict(
        app=app,
        db=db,
        add_prices=add_prices,
        add_ticker_prices=add_chunked_prices,
        Ticker=Ticker,
        Price=Price,
        UpdatesLog=UpdatesLog,
        utils=utils,
    )
    return kwargs


manager.add_command("db", MigrateCommand)
manager.add_command("runserver", server)
manager.add_command(
    "shell",
    Shell(banner=BANNER,make_context=_make_context)
)


if __name__ == '__main__':
    manager.run()
