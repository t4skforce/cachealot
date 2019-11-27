.PHONY: all clean build run

all: clean build run

compose: build up

clean:
	@echo "cleaning things"
	docker kill cachealot && echo "stopped container" || /bin/true
	docker rm cachealot && echo "removed container" || /bin/true
	docker rmi t4skforce/cachealot:latest && echo "removed container image" || /bin/true
	test -f ./env.list || cat Dockerfile | grep 'ENV' | sed 's/ENV //' > ./env.list

build:
	@echo "building things"
	docker build -t t4skforce/cachealot:latest .

run:
	@echo "runing things"
	docker run --name cachealot --env-file=./env.list -it --rm t4skforce/cachealot:latest

debug:
	@echo "runing in debug mode"
	docker run --name cachealot --env-file=./env.list  -v `pwd`/app/src/cachealot:/usr/lib/python3.7/site-packages/cachealot-0.0.1-py3.7.egg/cachealot:ro --entrypoint sh -it --rm t4skforce/cachealot:latest

dev:
	@echo "runing in dev mode"
	docker run --name cachealot --env-file=./env.list -v `pwd`/app/src/cachealot:/usr/lib/python3.7/site-packages/cachealot-0.0.1-py3.7.egg/cachealot:ro --entrypoint cachealot-cli -it --rm t4skforce/cachealot:latest

up:
	@echo "runing cachealot with elasticsearch and grafana"
	docker-compose -f docker-compose.yml stop || /bin/true
	docker-compose -f docker-compose.yml up
