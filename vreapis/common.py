import logging
import urllib3
import os
import requests.adapters

project_root = os.path.dirname(os.path.abspath(__file__))

# customized requests.Session [w/ auto retry]
session = requests.Session()
retry_adapter = requests.adapters.HTTPAdapter(max_retries=urllib3.Retry(total=10, backoff_factor=0.1, backoff_max=2, status_forcelist=[500, 502, 503, 504]))
session.mount('http://', retry_adapter)
session.mount('https://', retry_adapter)

# global logger
logger = logging.getLogger(__name__)
