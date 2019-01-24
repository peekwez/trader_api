# _*_ coding: utf-8 -*-
import warnings
warnings.simplefilter(action="ignore", category=Warning)

from flask_script import Manager, Shell, Server, prompt, prompt_pass
from flask_migrate import Migrate, MigrateCommand
from flask_jwt_extended import create_access_token, create_refresh_token

from trader import app
from extensions import db, jwt, ma
from models import Ticker, Price, UpdatesLog, User, TokenBlackList
from tasks import add_prices, add_chunked_prices
from constants import BANNER

from datetime import datetime
import utils
import random

manager = Manager(app)
shell = Shell(use_ipython=True)
server = Server(host="localhost",port=5000)
migrate = Migrate(app, db)

@manager.shell
def _make_context():
    kwargs = dict(
        app=app,
        db=db,
        jwt=jwt,
        ma=ma,
        add_prices=add_prices,
        add_ticker_prices=add_chunked_prices,
        Ticker=Ticker,
        Price=Price,
        User=User,
        TokenBlackList=TokenBlackList,
        UpdatesLog=UpdatesLog,
        utils=utils,
    )
    return kwargs


manager.add_command("db", MigrateCommand)
manager.add_command("runserver", server)
manager.add_command("shell",
    Shell(banner=BANNER,make_context=_make_context)
)

@manager.command
def create_admin_user():
    print("\n"+50*"*"+"\n")
    print("\t Create Trader API Admin User\n")
    print(50*"*" + "\n")

    data = dict()
    data["first_name"] = prompt("==> Enter your first name ", default=None)
    data["last_name"] = prompt("==> Enter your last name ", default=None)
    data["email"]  = prompt("==> Enter your email address ", default=None)
    data["password"] = prompt_pass("==> Enter your password ", default=None)
    confirm = ""

    max_retry = 1
    while data["password"] != confirm:
        if max_retry > 3:
            print("Maximum retries (3x) exceed, start again!")
            break
        confirm = prompt_pass("==> Confirm your password ", default=None)
        max_retry += 1


    user = User.find_by_email(data["email"])
    if max_retry <= 3 and not user:
        try:
            # create and save user
            user = User.create_user(data)
            user.is_admin = True
            user.last_login = datetime.now()
            user.date_joined = user.last_login
            user.save_to_db()

            # get tokens
            access_token  = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)

            # add tokens
            TokenBlackList.add_token(access_token)
            TokenBlackList.add_token(refresh_token)

            message = "\nUser <{0} {1}> was created!\n".format(
                data["first_name"],
                data["last_name"]
            )
        except:
            message = "\nSomething went wrong\n"
        finally:
            print(message)

@manager.command
def generate_secret_key(length=50):
    string = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    result = "".join([random.choice(string) for i in range(length)])
    return result


if __name__ == '__main__':
    manager.run()
