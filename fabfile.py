# _*_ coding: utf-8 -*-
from __future__ import absolute_import

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
        if results.exited is 0: add2list(c)
