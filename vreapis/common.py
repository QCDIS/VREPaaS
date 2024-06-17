import logging
import urllib3
import os
import requests.adapters

max_retry_count: int = 10
initial_retry_delay: int | float = 0.1
max_retry_delay: int | float = 5

default_varchar_length: int = 4000

project_root: str = os.path.dirname(os.path.abspath(__file__))

# customized requests.Session [w/ auto retry]
session = requests.Session()
retry_adapter = requests.adapters.HTTPAdapter(max_retries=urllib3.Retry(total=max_retry_count, backoff_factor=initial_retry_delay, backoff_max=max_retry_delay, status_forcelist=[500, 502, 503, 504]))
session.mount('http://', retry_adapter)
session.mount('https://', retry_adapter)

# global logger
logger = logging.getLogger(__name__)


def retry_delay(cumulated_retry_count: int, initial_delay: int | float = initial_retry_delay, max_delay: int | float = max_retry_delay) -> int | float:
    """delay is in seconds"""
    return min(initial_delay * 2 ** cumulated_retry_count, max_delay)
