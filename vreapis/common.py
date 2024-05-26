import logging
import urllib3
import requests.adapters

# customized requests.Session [w/ auto retry]
session = requests.Session()
retry_adapter = requests.adapters.HTTPAdapter(max_retries=urllib3.Retry(total=10, status_forcelist=[500]))
session.mount('http://', retry_adapter)
session.mount('https://', retry_adapter)

# global logger
logger = logging.getLogger(__name__)
