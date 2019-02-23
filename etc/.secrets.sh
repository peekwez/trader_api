#!/bin/bash
export SECRET_KEY='^d8d@fwd9g%i4^tpk$(x+)#p6hhdzc^nb((sa^$f#4dgkkcwd)'
export JWT_SECRET_KEY='9@k91w*oz1*ck)#*ahtultakva@yckw-@%sx-rvl^t+okg6z(o'

export HOSTNAME='localhost'

export POSTGRES_HOST=$HOSTNAME
export POSTGRES_PORT='5432'
export POSTGRES_DB='shawshank'
export POSTGRES_USER='postgres'
export POSTGRES_PASS='password'


export RABBIT_HOST=$HOSTNAME
export RABBIT_PORT='5672'
export RABBIT_VHOST='trader'
export RABBIT_USER='rabbit'
export RABBIT_PASS='password'

export REDIS_HOST=$HOSTNAME
export REDIS_PORT='6379'
export REDIS_DB='3'

export MEMCACHED_HOST=$HOSTNAME
export MEMCACHED_PORT='11211'
