include Make.in

# docker compose services
data-dep:
	$(call _info, Starting data dependency services)
	docker-compose -p data up -d db redis rabbit memcached

data: data-dep
	$(call _info, Starting app and web servers)
	cp requirements.txt services/app/
	docker-compose -p data up -d app web


# kill all running ports
killports:
	sudo fuser -k 5000/tcp 5554/tcp 5555/tcp 5556/tcp 5557/tcp
