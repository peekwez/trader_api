# _*_ coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys
import pdb
import collections
from contextlib import contextmanager

from fabric import Connection
from invoke import task



# django settings path
#django.settings_module('trucking.settings')

# fabric environment variables
#env.use_ssh_config = True
#env.shell = "/bin/bash -l -i -c"
#env.pwd = 'trucking'
#env.host_string = 'trucking'
#env.repo_url = 'git@github.com:peekwez/trucking.git'
#env.branch = 'develo
# codes
#command = '. /usr/share/virtualenvwrapper/virtualenvwrapper.sh;'
#command = 'workon trucking'
@contextmanager
def virtualenvwrapper(c):
    envcommand = 'source ~/.virtualenvs/trucking/bin/activate'
    with c.prefix(envcommand):
        yield


def add2list(c):
    'Updates the requirements file'
    c.run('pip freeze>requirements.txt')

@task
def addlib(c,name):
    with virtualenvwrapper(c):
        results = c.run('pip install {0} '.format(name))
        if results.exited is 0: add2list(c)