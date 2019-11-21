#!/usr/bin/env python

import os
import sys
import click
from .cachealot import Cachealot

@click.command()
@click.option('--interval', prompt='interval', type=click.IntRange(0), default=lambda: os.environ.get('CACHEALOT_INTERVAL', 5), help='Number of minutes to wait between warmup runs')
@click.option('--threads', prompt='threads', type=click.IntRange(0), default=lambda: os.environ.get('CACHEALOT_THREADS', 2), help='Number of threads to use for warmup')
@click.option('--entrypoint', prompt='entrypoint', type=click.STRING, default=lambda: os.environ.get('CACHEALOT_ENTRYPOINT'), help='url we find index page so we can extract the urls to call')
@click.option('--query', prompt='query', type=click.STRING, default=lambda: os.environ.get('CACHEALOT_QUERY', 'a'), help='pyquery expression to fetch new urls')
@click.option('--samedomain/--no-samedomain', prompt='samedomain', default=lambda: os.environ.get('CACHEALOT_SAMEDOMAIN', True), required=False, help='Allow other domains to be requested')
@click.option('--max-levels', prompt='max-levels', type=click.IntRange(-1), default=lambda: os.environ.get('CACHEALOT_MAX_LEVELS', -1), help='Maximum levels to request')
@click.option('--static/--no-static', prompt='static', default=lambda: os.environ.get('CACHEALOT_STATIC', True), help='Download static resources')
@click.option('--connection-timeout', prompt='connection-timeout', type=click.FLOAT, default=lambda: os.environ.get('CACHEALOT_CONNECTION_TIMEOUT', 120.0), help='HTTP connection timeout in seconds')
@click.option('--read-timeout', prompt='read-timeout', type=click.FLOAT, default=lambda: os.environ.get('CACHEALOT_READ_TIMEOUT', 120.0), help='HTTP read timeout in seconds')
@click.option('--user-agent', prompt='user-agent', type=click.STRING, default=lambda: os.environ.get('CACHEALOT_USER_AGENT','Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'), help='User-Agent header to use for requests')
@click.option('--elastic-search', type=click.STRING, default=lambda: os.environ.get('CACHEALOT_ELASTIC_SEARCH'), help='Address of Elastic-Search Server')
def entrypoint(interval, threads, entrypoint, query, samedomain, max_levels, static, connection_timeout, read_timeout, user_agent, elastic_search):
	try:
		Cachealot(interval, threads, entrypoint, query, samedomain, max_levels, static, connection_timeout, read_timeout, user_agent, elastic_search).run()
	except KeyboardInterrupt:
		sys.exit(0)

def main():
	entrypoint(auto_envvar_prefix='CACHEALOT')

def interactive():
	entrypoint()

if __name__ == '__main__':
	entrypoint()
