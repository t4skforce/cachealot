.PHONY: all clean build run

all: clean build run

clean:
	@echo "cleaning things"
	docker kill cachealot && echo "stopped container" || /bin/true
	docker rm cachealot && echo "removed container" || /bin/true
	docker rmi cachealot:latest && echo "removed container image" || /bin/true
	test -f ./env.list || cat Dockerfile | grep 'ENV' | sed 's/ENV //' > ./env.list

build:
	@echo "building things"
	docker build -t cachealot:latest .

run:
	@echo "runing things"
	docker run --name cachealot --network=elk_default --env-file=./env.list -it --rm cachealot:latest

debug:
	@echo "runing in dev mode"
	docker run --name cachealot --network=elk_default --env-file=./env.list -v `pwd`/app:/app:rw --entrypoint sh -it --rm cachealot:latest

dev:
	@echo "runing in dev mode"
	docker run --name cachealot --network=elk_default --env-file=./env.list -v `pwd`/app/src/cachealot:/usr/lib/python3.7/site-packages/cachealot-0.0.1-py3.7.egg/cachealot:ro --entrypoint cachealot-cli -it --rm cachealot:latest
