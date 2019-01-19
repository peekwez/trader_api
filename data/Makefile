host?=localhost
port?=5000

include Makefile.in

help:
	@echo "Choose 'make <target>' where target is one of the following:"
	@echo ""
	@echo "----------------------------"
	@echo " setup         Start docker services, create database and log files"
	@echo " process-logs  Create log files"
	@echo " dep-services  Start postgres, redis, rabbitmq and memcahced docker services"
	@echo " flower        Start celery flower on port 5012"
	@echo " notebook      Start ipython notebook on port 5011"
	@echo " worker        Start celery worker"
	@echo " beat          Start celery beat"
	@echo " processes     Start circus watchers in background"
	@echo " restart       Restart circus watchers"
	@echo " status        Check status of circus watchers"
	@echo " stopall       Stop all circus watchers"
	@echo " database      Create and migrate Flask app to database"
	@echo " createdb      Create database"
	@echo " migrate       Create Flask app to migrations"
	@echo " upgrade       Migrate Flaks app migrations"
	@echo " graphmodels   Graph and save Django app models"
	@echo " runserver     Start Flask development server on port 5000"
	@echo ""

# run unit tests
#tests: removecache
#	$(call _info, Running unit tests)
#	py.test -vv --cov-config=setup.cfg --cov=src $(test_db) src


# setup application
setup: web-services database process-logs


# create log files
process-logs:
	$(call _info, Creating log files)
	rm -fr logs; \
	mkdir -p logs; cd logs; \
	touch flower.log beat.log worker.log \
	app.log dev.log circus.log book.log \
	pgadmin.log access.log error.log


# docker compose services
dep-services:
	$(call _info, Starting dependency services)
	docker-compose -p data up -d db redis rabbit memcached

web-services: dep-services
	$(call _info, Starting app and web servers)
	cp requirements.txt services/app/
	docker-compose -p data up -d app web

dev-services: dep-services
	$(call _info, Starting development server)
	cp requirements.txt services/app/
	docker-compose -p data up dev

# process manager
circus: process-logs
	$(call _info, Starting circus watchers)
	circusd circus.ini --daemon --log-level info --log-output logs/circus.log

restart:
	$(call _info, Restarting circus watcher)
	circusctl restart

status:
	$(call _info, Status of circus watchers)
	circusctl status

stopall:
	$(call _info, Stoping all circus watchers)
	circusctl stop

# watcher commands
chaussette:
	$(call _info, Starting app server with Chaussette)
	chaussette --port=5000 --backend meinheld run.app --log-level=info

flower:
	$(call _info, Starting celery flower on port 5012)
	celery flower -A tasks.app -l info --port=5012 --pool gevent


notebook:
	$(call _info, Starting jupyter notebook on port 5011)
	jupyter-notebook --port=5011

worker:
	$(call _info, Starting celery worker)
	celery worker -A tasks.app -l info

beat:
	$(call _info, Starting celery beat)
	celery beat -A tasks.app -l info --pidfile='logs/beat.pid'


# database commands
database: createdb init migrate upgrade

createdb:
	$(call _info, Creating database)
	dropdb -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) $(DB_NAME) --if-exists
	createdb -h $(DB_HOST) -p $(DB_PORT) -U $(DB_USER) $(DB_NAME)

upgrade:
	$(call _info, Apply migrations to Flask app database)
	python -W ignore manage.py db upgrade

downgrade:
	$(call _info, Drop migrations for Flask app database)
	python -W ignore manage.py db downgrade

migrate:
	$(call _info, Create migration for Flask app database)
	python -W ignore manage.py db migrate

init:
	$(call _info, Initialize database migrations)
	python -W ignore manage.py db init

createsu:
	$(call _info, Creating admin user for Trader app)
	python -W ignore manage.py create_admin_user

#graphmodels:
#	$(call _info, Graphing Django app models)
#	cd src && python manage.py graph_models --pygraphviz -a -g -o graphed_models.png


# development server
runserver:
	$(call _info, Start server with Werkzeug debugger)
	export FLASK_ENV=development && \
	python -W ignore manage.py runserver --port=$(port) --host=$(host)


# start shell
shell:
	$(call _info, Starting ipython shell)
	python -W ignore manage.py shell


# miscellaneous
tree:
	$(call _info, Showing directory structure for project)
	tree -I '*.pyc|*.ipynb|*pycache*|logs|static|secrets*|*.pid|*schedule|*.png|00*'

addstatic:
	$(call _info, Collecting static files)
	mkdir static media
#       cd src && python manage.py collectstatic --noinput

removecache:
	$(call _info, Removing pytest cache)
	find . | grep -E "(__pycache__)" | xargs rm -rf
	rm -fr .cache

killports:
	sudo fuser -k 5000/tcp 5001/tcp 5002/tcp 5003/tcp 5004/tcp 5555/tcp
