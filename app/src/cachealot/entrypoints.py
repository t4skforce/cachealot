#!/usr/bin/env python

import os
import click
import requests
import pyquery
from .cachealot import Cachealot

CACHEALOT_INTERVAL = int(os.getenv('CACHEALOT_INTERVAL', 5))
CACHEALOT_THREADS = int(os.getenv('CACHEALOT_THREADS', 4))
CACHEALOT_ENTRYPOINT = str(os.getenv('CACHEALOT_ENTRYPOINT', 'https://pypy.org'))
CACHEALOT_QUERY = str(os.getenv('CACHEALOT_QUERY', '#menu-sub a'))
CACHEALOT_ATTR = str(os.getenv('CACHEALOT_ATTR', 'href'))
CACHEALOT_SAMEDOMAIN = str(os.getenv('CACHEALOT_SAMEDOMAIN', 'true')).lower() in ['true', '1', 'y', 'yes' ]
CACHEALOT_LEVELS = int(os.getenv('CACHEALOT_LEVELS', -1))
CACHEALOT_CONNECTION_TIMEOUT = float(os.getenv('CACHEALOT_CONNECTION_TIMEOUT', 120.0))
CACHEALOT_READ_TIMEOUT = float(os.getenv('CACHEALOT_READ_TIMEOUT', 120.0))


@click.command()
@click.option("--interval", default=CACHEALOT_INTERVAL, help="Number of minutes to wait between warmup runs")
@click.option("--threads", default=CACHEALOT_THREADS, help="Number of threads to use for warmup")
@click.option("--entrypoint", default=CACHEALOT_ENTRYPOINT, help="url we find index page so we can extract the urls to call")
@click.option("--query", default=CACHEALOT_QUERY, help="pyquery expression to fetch navigation links")
@click.option("--attr", default=CACHEALOT_ATTR, help="pyquery attribute to extract the url")
@click.option('--no-samedomain', is_flag=True, default=CACHEALOT_SAMEDOMAIN, required=False, help="Allow other domains to be requested")
@click.option('--max-levels', default=CACHEALOT_LEVELS, help="Maximum levels to request")
@click.option('--connection-timeout', default=CACHEALOT_CONNECTION_TIMEOUT, help="HTTP connection timeout in seconds")
@click.option('--read-timeout', default=CACHEALOT_READ_TIMEOUT, help="HTTP read timeout in seconds")
def main(interval, threads, entrypoint, query, attr, no_samedomain, max_levels, connection_timeout, read_timeout):
	Cachealot(interval, threads, entrypoint, query, attr, no_samedomain, max_levels, connection_timeout, read_timeout).run()


@click.command()
@click.option("--interval", default=CACHEALOT_INTERVAL, prompt='interval', help="Number of minutes to wait between warmup runs")
@click.option("--threads", default=CACHEALOT_THREADS, prompt='threads', help="Number of threads to use for warmup")
@click.option("--entrypoint", default=CACHEALOT_ENTRYPOINT, prompt='entrypoint', help="url we find index page so we can extract the urls to call")
@click.option("--query", default=CACHEALOT_QUERY, prompt='query', help="pyquery expression to fetch navigation links")
@click.option("--attr", default=CACHEALOT_ATTR, prompt='attr', help="pyquery attribute to extract the url")
@click.option('--no-samedomain', is_flag=True, default=CACHEALOT_SAMEDOMAIN, required=False, prompt='samedomain', help="Allow other domains to be requested")
@click.option('--max-levels', default=CACHEALOT_LEVELS, prompt='max-levels', help="Maximum levels to request")
@click.option('--connection-timeout', default=CACHEALOT_CONNECTION_TIMEOUT, prompt='connection-timeout', help="HTTP connection timeout in seconds")
@click.option('--read-timeout', default=CACHEALOT_READ_TIMEOUT, prompt='read-timeout', help="HTTP read timeout in seconds")
def interactive(interval, threads, entrypoint, query, attr, no_samedomain, max_levels, connection_timeout, read_timeout):
	Cachealot(interval, threads, entrypoint, query, attr, no_samedomain, max_levels, connection_timeout, read_timeout).run()

if __name__ == '__main__':
	interactive()
