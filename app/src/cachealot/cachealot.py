#!/usr/bin/env python

from concurrent.futures import ThreadPoolExecutor, wait, as_completed
import requests
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore',InsecureRequestWarning)
from requests.exceptions import Timeout
from pyquery import PyQuery as pq
import time
import json
from urllib.parse import urlparse, urljoin, parse_qs
from datetime import datetime, timedelta
import tldextract
import socket
import base64
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - [%(levelname)s] %(message)s', level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

class Cachealot:
	def __init__(self, interval, threads, entrypoint, query, samedomain, levels, static, connection_timeout, read_timeout, user_agent, elastic_search):
		logger.info('Settings: {}'.format({
			"interval":interval,
			"threads":threads,
			"entrypoint":entrypoint,
			"query":query,
			"samedomain":samedomain,
			"levels":levels,
			"static":static,
			"connection-timeout":connection_timeout,
			"read-timeout":read_timeout,
			"user-agent":user_agent,
			"elastic-search":elastic_search
		}))
		self.interval = interval
		self.threads = threads
		self.entrypoint = entrypoint
		self.query = query
		if static == True: 
			self.query = '{},img,link[rel="stylesheet"],script'.format(query)
		self.samedomain = samedomain
		self.levels = levels
		self.timeout = (connection_timeout,read_timeout)
		o = urlparse(self.entrypoint)
		self.base_domain = o.netloc.split(':')[0]
		if '/' in o.path: 
			self.base_path = o.path[:o.path.rindex('/')+1]
		else:
			self.base_path = '/'
		self.base_depth = len(self.base_path.split('/'))
		self.user_agent = user_agent
		self.elastic_search = elastic_search
		if not self.elastic_search is None:
			while True:
				try:
					if requests.get(self.elastic_search).status_code == 200: 
						break
				except: 
					pass
				logger.info('waiting for elk to come up')
				time.sleep(5)
			self.set_up_elk()

	def set_up_elk(self):
		if requests.get(urljoin(self.elastic_search,'/_ilm/policy/cachealot_cleanup_policy')).json().get('cachealot_cleanup_policy',None) is None:
			requests.put(urljoin(self.elastic_search,'/_ilm/policy/cachealot_cleanup_policy?pretty'), json={"policy":{"phases":{"hot":{"actions":{}},"delete":{"min_age":"30d","actions":{"delete":{}}}}}},verify=False)
			requests.put(urljoin(self.elastic_search,'/_template/cachealot_logging_policy_template?pretty'), json={"index_patterns": ["cachealot-*"],"settings":{"index.lifecycle.name":"cachealot_cleanup_policy"}},verify=False)

	def log_elk(self,url,start,end,r):
		o = urlparse(url)
		tld = tldextract.extract(url)
		r = requests.post(urljoin(self.elastic_search,'/cachealot-{}/entries/?pretty'.format(time.strftime('%Y%m%d', time.localtime(start)))),json={
			'@timestamp':time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(start)),
			'@finished':time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(end)),
			'@hostname': str(socket.gethostname()),
			'status':int(r.status_code),
			'headers': json.loads(str(r.headers).replace("'",'"')),
			'cookies': r.cookies.get_dict(),
			'url': url,
			'responseurl': str(r.url),
			'scheme': o.scheme,
			'hostname': o.hostname,
			'netloc': o.netloc,
			'ip': socket.gethostbyname(o.netloc),
			'tld':{'subdomain':tld.subdomain,'domain':tld.domain,'suffix':tld.suffix},
			'path': o.path,
			'paths': [x for x in o.path.split("?", 1)[0].split("/") if x != "" ],
			'query': o.query,
			'queryparams': parse_qs(o.query),
			'port': o.port,
			'size': len(r.content),
			'time': end-start
		}, verify=False)

	def request(self, url, timeout):
		try:
			start = time.time()
			try:
				r = requests.get(url, timeout=timeout, verify=False, headers={'User-Agent': self.user_agent})
				end = time.time()
				if not self.elastic_search is None:
					#self.log_elk(url,start,end,r)
					self.export_pool.submit(self.log_elk,url,start,end,r)
				if r.status_code == 200:
					logger.info('HTTP[{}] ({}/{:.2f}s) {}'.format(r.status_code,sizeof_fmt(len(r.text)),(end-start),url))
					if "text/" in r.headers["content-type"]:
						return r.content
				else:
					logger.error('HTTP[{}] ({:.2f}s) {}'.format(r.status_code,(end-start),url))
			except Timeout:
				end = time.time()
				logger.error('Timeout ({:.2f}s) {}'.format((end-start),url))
		except:
			logger.exception('request error')
		return None

	def get_full_url(self, url):
		if not url is None:
			url = url.strip()
			if len(url) > 0:
				target = urljoin(self.entrypoint, url).split("#", 1)[0]
				try:
					o = urlparse(target)
					target_domain = o.netloc.split(':')[0]
					target_path = '/'
					if '/' in o.path: target_path = o.path[:o.path.rindex('/')]
					target_depth = len(target_path.split('/'))
					if self.samedomain == False or (self.samedomain and target_domain == self.base_domain):
						if self.levels == -1 or (target_path.startswith(self.base_path) and len(target_path[len(self.base_path):].split('/')) <= self.levels):
							yield target
				except:
					pass

	def get_url_from_elem(self, elem):
		if elem.is_('a'): return elem.attr('href')
		if elem.is_('img'): return elem.attr('src') or elem.attr('data-src')
		if elem.is_('link'): return elem.attr('href')
		if elem.is_('script'): return elem.attr('src')
		if elem.is_('iframe'): return elem.attr('src')
		if elem.is_('source'): return elem.attr('src')

	def extract_urls(self, content):
		try:
			if not content is None:
				q = pq(content)
				for elem in q(self.query).items():
					for url in self.get_full_url(self.get_url_from_elem(elem)):
						yield url
		except:
			logger.exception('extract_urls error')

	def run(self):
		try:
			with ThreadPoolExecutor(max_workers=4) as self.export_pool:
				while True:
					start = time.time()
					links = set()
					futures = set()
					with ThreadPoolExecutor(max_workers=self.threads) as pool:
						futures.add(pool.submit(self.request, self.entrypoint, self.timeout))
						while len(futures) > 0:
							for future in as_completed(futures):
								try:
									for link in self.extract_urls(future.result()):
										if not link in links:
											logger.info('new: {}'.format(link))
											links.add(link)
											futures.add(pool.submit(self.request, link, self.timeout))
								finally:
									futures.remove(future)
					end = time.time()
					logger.info('finished requesting {} pages in {}'.format(len(links)+1,str(timedelta(seconds=end - start))))
					logger.info('sleeping for {}'.format(str(timedelta(seconds=self.interval*60))))
					time.sleep(self.interval*60)
		except KeyboardInterrupt:
			pass
		except:
			logger.exception('URL={}'.format(self.entrypoint))
			
