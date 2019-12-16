#!/usr/bin/env python

import os
import sys
import click
from .options import Options
from .cachealot import Cachealot

@click.command()
@click.option('--interval', prompt='interval', type=click.IntRange(-1), default=lambda: os.environ.get('CACHEALOT_INTERVAL', 5), help='Number of minutes to wait between warmup runs')
@click.option('--threads', prompt='threads', type=click.IntRange(1), default=lambda: os.environ.get('CACHEALOT_THREADS', 2), help='Number of threads to use for warmup')
@click.option('--entrypoint', prompt='entrypoint', type=click.STRING, default=lambda: os.environ.get('CACHEALOT_ENTRYPOINT'), help='url we find index page so we can extract the urls to call')
@click.option('--query', prompt='query', type=click.STRING, default=lambda: os.environ.get('CACHEALOT_QUERY', 'a'), help='pyquery expression to fetch new urls')
@click.option('--sitemap', type=click.STRING, default=lambda: os.environ.get('CACHEALOT_SITEMAP', None), help='location of the sitemap.xml can be None to ignore sitemap.xml')
@click.option('--blacklist', type=click.STRING, default=lambda: os.environ.get('CACHEALOT_BLACKLIST', None), help='blacklist urls nased on a regex pattern')
@click.option('--samedomain/--no-samedomain', prompt='samedomain', default=lambda: os.environ.get('CACHEALOT_SAMEDOMAIN', True), required=False, help='Allow other domains to be requested')
@click.option('--max-levels', prompt='max-levels', type=click.IntRange(-1), default=lambda: os.environ.get('CACHEALOT_MAX_LEVELS', -1), help='Maximum levels to request')
@click.option('--static/--no-static', prompt='static', default=lambda: os.environ.get('CACHEALOT_STATIC', True), help='Download static resources')
@click.option('--http-proxy', type=click.STRING, default=lambda: os.environ.get('CACHEALOT_HTTP_PROXY',None), help='HTTP Proxy-Server to use')
@click.option('--https-proxy', type=click.STRING, default=lambda: os.environ.get('CACHEALOT_HTTP_PROXY',None), help='HTTPS Proxy-Server to use')
@click.option('--connection-timeout', prompt='connection-timeout', type=click.FLOAT, default=lambda: os.environ.get('CACHEALOT_CONNECTION_TIMEOUT', 120.0), help='HTTP connection timeout in seconds')
@click.option('--read-timeout', prompt='read-timeout', type=click.FLOAT, default=lambda: os.environ.get('CACHEALOT_READ_TIMEOUT', 120.0), help='HTTP read timeout in seconds')
@click.option('--user-agent', prompt='user-agent', type=click.STRING, default=lambda: os.environ.get('CACHEALOT_USER_AGENT','Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'), help='User-Agent header to use for requests')
@click.option('--headers', type=click.STRING, default=lambda: os.environ.get('CACHEALOT_HEADERS',None), help='HTTP-Headers to send with the requests')
@click.option('--elastic-search', type=click.STRING, default=lambda: os.environ.get('CACHEALOT_ELASTIC_SEARCH',None), help='Address of Elastic-Search Server')
@click.option('--kibana', type=click.STRING, default=lambda: os.environ.get('CACHEALOT_KIBANA',None), help='Address of Kibana Server')
def entrypoint(interval, threads, entrypoint, query, sitemap, blacklist, samedomain, max_levels, static, http_proxy, https_proxy, connection_timeout, read_timeout, user_agent, headers, elastic_search, kibana):
	try:
		options = Options()
		options.interval = interval
		options.threads = threads
		options.entrypoint = entrypoint
		options.query = query
		options.sitemap = sitemap
		options.blacklist = blacklist
		options.samedomain = samedomain
		options.max_levels = max_levels
		options.static = static
		options.http_proxy = http_proxy
		options.https_proxy = https_proxy
		options.connection_timeout = connection_timeout
		options.read_timeout = read_timeout
		options.user_agent = user_agent
		options.headers = headers
		options.elastic_search = elastic_search
		options.kibana = kibana
		Cachealot(options).run()
	except KeyboardInterrupt:
		sys.exit(0)

def main():
	entrypoint(auto_envvar_prefix='CACHEALOT')

def interactive():
	entrypoint()

if __name__ == '__main__':
	entrypoint()
