#_*_ coding: utf-8 -*-

import factory
import random
from faker import Faker
from faker.providers import BaseProvider


import models as md
import extensions as ext
from assets import tickers

sample = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
sample += "abcdefghijklmnopqrstuvwxyz"
sample += "0123456789!@#$%^&*(-_=+)"
df = tickers.get("nasdaq")

def _get_password(length=10):
    result = "".join([random.choice(sample) for i in range(length)])
    return result

class Provider(BaseProvider):
    def password(self):
        return _get_password()

    def ticker(self,pk,field):
        f = df.iloc[[pk]][field]
        return f.values[0]


fake = Faker()
fake.add_provider(Provider)

# base factory
class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = ext.db.session

# user factory
class UserFactory(BaseFactory):

    class Meta:
        model = md.User

    first_name= fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    password = fake.password()
    is_admin = False

# admin user factory
class AdminFactory(BaseFactory):

    class Meta:
        model = md.User

    first_name= fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    password = fake.password()
    is_admin = True

# ticker factory
class TickerFactory(BaseFactory):

    class Meta:
        model = md.Ticker

    name = factory.Sequence(lambda n:fake.ticker(n,"name"))
    symbol = factory.Sequence(lambda n:fake.ticker(n,"symbol"))
    sector = factory.Sequence(lambda n:fake.ticker(n,"sector"))
    industry = factory.Sequence(lambda n:fake.ticker(n,"exchange"))
    market = factory.Sequence(lambda n:fake.ticker(n,"market"))
    type = factory.Sequence(lambda n:fake.ticker(n,"type"))
