# _*_ coding: utf-8 -*-

import os
import sys
import pdb
import collections
from contextlib import contextmanager

from fabric import Connection
from invoke import task



@contextmanager
def envwrapper(c):
    envcommand = 'source ~/.virtualenvs/trader/bin/activate'
    with c.prefix(envcommand):
        yield


def freeze(c):
    'Updates the requirements file'
    c.run('pip freeze>requirements.txt')

@task
def install(c,name):
    with envwrapper(c):
        results = c.run('pip install {0} '.format(name))
        if results.exited is 0: freeze(c)

@task
def server(c,env="development"):
    with envwrapper(c):
        command  = "export FLASK_ENV={0}".format(env)
        command += " && python run.py"
        c.run(command)

@task
def initdb(c):
    with envwrapper(c):
        c.run("rm -fr app.db migrations/")
        c.run("python migrate.py db init")

@task
def migratedb(c):
    with envwrapper(c):
        command  = "python migrate.py db migrate"
        c.run(command)

@task
def updatedb(c):
    with envwrapper(c):
        command  = "python migrate.py db upgrade"
        c.run(command)
