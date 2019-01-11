#!/bin/bash
export HOSTNAME='localhost'

export DB_NAME='shawshank'
export DB_USER='postgres'
export DB_PASS='password'
export DB_HOST=$HOSTNAME
export DB_PORT='5432'

export RABBIT_DEFAULT_USER='rabbitmq'
export RABBIT_DEFAULT_PASS='rabbitmq'
export RABBIT_DEFAULT_VHOST='shawshank'
export RABBIT_HOST=$HOSTNAME
export RABBIT_PORT='5672'

export REDIS_HOST=$HOSTNAME
export REDIS_PORT='6379'

export MEMCACHED_HOST=$HOSTNAME
export MEMCACHED_PORT='11211'
