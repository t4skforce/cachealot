#!/usr/bin/env python

import os
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
	def __init__(self, options):
		self.o = options
		logger.info('Settings: {}'.format(str(self.o)))
		self.o.setup()
		

	def log_elk(self,url,start,end,response,source="index"):
		o = urlparse(url)
		tld = tldextract.extract(url)
		requests.post(urljoin(self.o.elastic_search,'/cachealot-{}/entries/?pretty'.format(time.strftime('%Y%m%d', time.localtime(start)))),json={
			'@timestamp':time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(start)),
			'@finished':time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(end)),
			'@hostname': str(socket.gethostname()),
			'@source': source,
			'status':int(response.status_code),
			'headers': json.loads(str(response.headers).replace("'",'"')),
			'cookies': response.cookies.get_dict(),
			'url': url,
			'responseurl': str(response.url),
			'history':[{
				'status':resp.status_code, 
				'url':resp.url, 
				'headers': json.loads(str(resp.headers).replace("'",'"')),
				'cookies': resp.cookies.get_dict(),
			} for resp in response.history] if response.history else [],
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
			'size': len(response.content),
			'time': end-start
		}, verify=False)

	def request(self, url, source="index"):
		try:
			start = time.time()
			try:
				response = requests.get(url, timeout=self.o.timeout, verify=False, headers=self.o.headers)
				end = time.time()
				if not self.o.elastic_search is None:
					#self.log_elk(url,start,end,r)
					self.log_elk(url,start,end,response,source)
					#self.export_pool.submit(self.log_elk,url,start,end,response,source)
				if response.status_code == 200:
					logger.info('HTTP[{}] ({}/{:.2f}s) {}'.format(response.status_code,sizeof_fmt(len(response.content)),(end-start),url))
					if "text/" in response.headers["content-type"]:
						return response
				else:
					logger.error('HTTP[{}] ({:.2f}s) {}'.format(response.status_code,(end-start),url))
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
				target = urljoin(self.o.entrypoint, url).split("#", 1)[0]
				try:
					o = urlparse(target)
					target_domain = o.netloc.split(':')[0]
					target_path = '/'
					if '/' in o.path: target_path = o.path[:o.path.rindex('/')]
					target_depth = len(target_path.split('/'))
					if self.o.samedomain == False or (self.o.samedomain and target_domain == self.o.base_domain):
						if self.o.levels == -1 or (target_path.startswith(self.o.base_path) and len(target_path[len(self.o.base_path):].split('/')) <= self.o.levels):
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
				for elem in q(self.o.query).items():
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
					with ThreadPoolExecutor(max_workers=self.o.threads) as pool:
						futures.add(pool.submit(self.request, self.o.entrypoint))
						while len(futures) > 0:
							for future in as_completed(futures):
								try:
									response = future.result()
									if not response is None:
										for link in self.extract_urls(response.content):
											if not link in links:
												logger.info('new: {}'.format(link))
												links.add(link)
												futures.add(pool.submit(self.request, link, response.url))
								finally:
									futures.remove(future)
					end = time.time()
					logger.info('finished requesting {} pages in {}'.format(len(links)+1,str(timedelta(seconds=end - start))))
					logger.info('sleeping for {}'.format(str(timedelta(seconds=self.o.interval*60))))
					if self.o.interval > -1:
						time.sleep(self.o.interval*60)
		except KeyboardInterrupt:
			pass
		except:
			logger.exception('URL={}'.format(self.o.entrypoint))
			
