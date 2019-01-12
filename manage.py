# _*_ coding: utf-8 -*-
import warnings
warnings.simplefilter(action="ignore", category=Warning)

from flask_script import Manager, Shell, Server, prompt, prompt_pass
from flask_migrate import Migrate, MigrateCommand

from run import app
from models import db, Ticker, Price, UpdatesLog, User
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


    if max_retry <= 3:
        try:
            user = User.create_user(data)
            user.is_admin = True
            user.save_to_db()
            message = "\nUser <{0} {1}> was created!\n".format(
                data["first_name"],
                data["last_name"]
            )
        except:
            message = "\nSomething went wrong\n"
        finally:
            print(message)




if __name__ == '__main__':
    manager.run()
