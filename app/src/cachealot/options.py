#!/usr/bin/env python
import os
import json
from urllib.parse import urlparse, urljoin
import requests
import time
import logging
import re
logging.basicConfig(format='%(asctime)s - %(name)s - [%(levelname)s] %(message)s', level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class Options:
	def __init__(self):
		self.interval = -1
		self.threads = 1
		self.entrypoint = 'https://pypy.org'
		self.query = 'a'
		self.sitemap = None
		self.samedomain = True
		self.blacklist = None
		self.levels = -1
		self.static = False
		self.connection_timeout = 60
		self.read_timeout = 60
		self.user_agent = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
		self.elastic_search = None
		self.kibana = None
		self.headers = dict()

	def _setup_elk(self):
		if not self.elastic_search is None:
			while True:
				try:
					if requests.get(self.elastic_search).status_code == 200: 
						break
				except: 
					pass
				logger.info('waiting for elasticsearch to come up')
				time.sleep(5)
			if requests.get(urljoin(self.elastic_search,'/_ilm/policy/cachealot_cleanup_policy')).json().get('cachealot_cleanup_policy',None) is None:
				requests.put(urljoin(self.elastic_search,'/_ilm/policy/cachealot_cleanup_policy?pretty'), json={"policy":{"phases":{"hot":{"actions":{}},"delete":{"min_age":"30d","actions":{"delete":{}}}}}},verify=False)
				requests.put(urljoin(self.elastic_search,'/_template/cachealot_logging_policy_template?pretty'), json={"index_patterns": ["cachealot-*"],"settings":{"index.lifecycle.name":"cachealot_cleanup_policy"}},verify=False)

	def _setup_kibana(self):
		if not self.kibana is None:
			while True:
				try:
					r = requests.get(urljoin(self.kibana, '/api/security/v1/me'))
					if r.status_code == 200 and not "not ready" in r.text:
						break
				except: 
					pass
				logger.info('waiting for kibana to come up')
				time.sleep(5)
			search = requests.get(urljoin(self.kibana,'/api/kibana/management/saved_objects/_find?search=cachealot&type=index-pattern')).json()
			if not search.get('saved_objects',None) is None and len(search.get('saved_objects')) == 0:
				r = requests.post(urljoin(self.kibana,'/api/saved_objects/_import?overwrite=true'),headers={'kbn-xsrf':'true'}, files={'file':open(os.path.join(os.path.dirname(__file__), 'data/export.ndjson'),'rb')})
				logger.info('restored objects: {}'.format(r.text))
				if r.json().get('success') != True:
					logger.error('error importing kibana data: {}'.format(r.text))
					time.sleep(10)

	def setup(self):
		self._setup_elk()
		self._setup_kibana()

	@property
	def interval(self):
		return self._interval

	@interval.setter
	def interval(self, interval):
		if not interval is None:
			if interval < 0:
				self._interval=-1
			else:
				self._interval=interval

	@property
	def threads(self):
		return self._threads

	@threads.setter
	def threads(self, threads):
		if not threads is None:
			if threads <= 0:
				self._threads=1
			else:
				self._threads=threads

	@property
	def entrypoint(self):
		return self._entrypoint

	@entrypoint.setter
	def entrypoint(self, entrypoint):
		if not entrypoint is None:
			o = urlparse(entrypoint)
			self._base_domain = o.netloc.split(':')[0]
			if '/' in o.path: 
				self._base_path = o.path[:o.path.rindex('/')+1]
			else: 
				self._base_path = '/'
			self._base_depth = len(self._base_path.split('/'))
			self._entrypoint = entrypoint

	@property
	def base_domain(self):
		return self._base_domain

	@property
	def base_path(self):
		return self._base_path

	@property
	def base_depth(self):
		return self._base_depth

	@property
	def query(self):
		if self._static == True:
			return '{},img,link[rel="stylesheet"],script'.format(self._query)
		return self._query

	@query.setter
	def query(self, query):
		if not query is None:
			self._query=query

	@property
	def sitemap(self):
		return self._sitemap

	@sitemap.setter
	def sitemap(self, sitemap):
		self._sitemap=sitemap

	@property
	def blacklist(self):
		return self._blacklist

	@blacklist.setter
	def blacklist(self, pattern):
		if not pattern is None:
			self._blacklist=re.compile(pattern, re.IGNORECASE | re.DOTALL)
		else:
			self._blacklist=None

	@property
	def samedomain(self):
		return self._samedomain == True

	@samedomain.setter
	def samedomain(self, samedomain):
		if not samedomain is None:
			self._samedomain=(samedomain == True)

	@property
	def levels(self):
		return self._levels

	@levels.setter
	def levels(self, levels):
		if not levels is None:
			if levels < 0:
				self._levels=-1
			else:
				self._levels=levels

	@property
	def static(self):
		return self._static == True

	@static.setter
	def static(self, static):
		if not static is None:
			self._static=(static == True)

	@property
	def connection_timeout(self):
		return self._connection_timeout

	@connection_timeout.setter
	def connection_timeout(self, connection_timeout):
		if not connection_timeout is None:
			if connection_timeout < 0:
				self._connection_timeout=-1
			else:
				self._connection_timeout=connection_timeout

	@property
	def read_timeout(self):
		return self._read_timeout

	@read_timeout.setter
	def read_timeout(self, read_timeout):
		if not read_timeout is None:
			if read_timeout < 0:
				self._read_timeout=-1
			else:
				self._read_timeout=read_timeout

	@property
	def timeout(self):
		return (self._connection_timeout,self._read_timeout)

	@property
	def user_agent(self):
		return self._user_agent

	@user_agent.setter
	def user_agent(self, user_agent):
		if not user_agent is None:
			self._user_agent=user_agent

	@property
	def elastic_search(self):
		return self._elastic_search

	@elastic_search.setter
	def elastic_search(self, elastic_search):
		self._elastic_search=elastic_search

	@property
	def kibana(self):
		return self._kibana

	@kibana.setter
	def kibana(self, kibana):
		self._kibana=kibana

	@property
	def headers(self):
		ret = dict()
		if not self.user_agent is None:
			ret['user-agent'] = self.user_agent
		if not self._headers is None:
			ret.update(self._headers)
		return ret

	@headers.setter
	def headers(self, headers):
		if not headers is None:
			# RFC 2616: Each header field consists of a name followed by a colon (":") and the field value. Field names are case-insensitive.
			if isinstance(headers, dict):
				self._headers = dict((k.lower(), v) for k,v in headers.items())
			elif isinstance(headers, str):
				print(headers)
				jobj = json.loads(str(headers))
				if isinstance(jobj, dict):
					self._headers = jobj

	def __str__(self):
		ret = list()
		for field in dir(self):
			if not field.startswith('_') and field != 'setup':
				ret.append('{}:{}'.format(field, getattr(self,field)))
		return ', '.join(ret)
	
	def __repr__(self):
		return 'Options({})'.format(self.__str__())

