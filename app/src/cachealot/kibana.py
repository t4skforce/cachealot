#!/usr/bin/env python

import os
import requests
from urllib.parse import urljoin

def setup_kibana(kibana):
	##requests.post(urljoin(kibana,'/api/saved_objects/index-pattern'), json={'attributes': {'title': 'cachealot-*', 'timeFieldName': "@timestamp", 'fields': '[]'}})
	## import using restore saved objects
	pass
	
