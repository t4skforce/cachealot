#!/usr/bin/env python

from concurrent.futures import ThreadPoolExecutor, wait, as_completed
import requests
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore',InsecureRequestWarning)
from requests.exceptions import Timeout
from pyquery import PyQuery as pq
import time
import datetime
from urllib.parse import urlparse, urljoin
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
	def __init__(self, interval, threads, entrypoint, query, attr, samedomain, levels, connection_timeout, read_timeout):
		self.interval = interval
		self.threads = threads
		self.entrypoint = entrypoint
		self.query = query
		self.attr = attr
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

	def request(self, url, timeout):
		try:
			start = time.time()
			try:
				r = requests.get(url, timeout=timeout, verify=False)
				end = time.time()
				if r.status_code == 200:
					logger.info('HTTP[{}] ({}/{:.2f}s) {}'.format(r.status_code,sizeof_fmt(len(r.text)),(end-start),url))
					return r.content
				else:
					logger.error('HTTP[{}] ({:.2f}s) {}'.format(r.status_code,(end-start),url))
			except Timeout:
				logger.error('Timeout ({:.2f}s) {}'.format((end-start),url))
		except:
			logger.exception('request error')
		return None

	def extract_urls(self, content):
		try:
			if not content is None:
				q = pq(content)
				for link in q(self.query).items():
					target = urljoin(self.entrypoint, link.attr[self.attr])
					o = urlparse(target)
					target_domain = o.netloc.split(':')[0]
					target_path = '/'
					if '/' in o.path: target_path = o.path[:o.path.rindex('/')]
					target_depth = len(target_path.split('/'))
					if self.samedomain == False or (self.samedomain and target_domain == self.base_domain):
						if self.levels == -1 or (target_path.startswith(self.base_path) and len(target_path[len(self.base_path):].split('/')) <= self.levels):
							yield target
		except:
			logger.exception('extract_urls error')

	def run(self):
		try:
			while True:
				start = time.time()
				links = set()
				futures = set()
				with ThreadPoolExecutor(max_workers=self.threads) as pool:
					futures.add(pool.submit(self.request, self.entrypoint, self.timeout))
					for future in as_completed(futures):
						for link in self.extract_urls(future.result()):
							if not link in links:
								logger.info('new: {}'.format(link))
								links.add(link)
								futures.add(pool.submit(self.request, link, self.timeout))
				end = time.time()
				logger.info('finished requesting {} pages in {}'.format(len(links)+1,str(datetime.timedelta(seconds=end - start))))
				logger.info('sleeping for {}'.format(str(datetime.timedelta(seconds=self.interval*60))))
				time.sleep(self.interval*60)
		except:
			logger.exception('URL={}'.format(self.entrypoint))
			
