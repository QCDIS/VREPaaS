import os
import logging
import requests
import requests.adapters
import urllib3
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

logger = logging.getLogger(__name__)

# customized requests.Session [w/ auto retry]
session = requests.Session()
retry_adapter = requests.adapters.HTTPAdapter(max_retries=urllib3.Retry(total=5, status_forcelist=[500]))
session.mount('http://', retry_adapter)
session.mount('https://', retry_adapter)


@api_view(['GET'])
def get_base_images(request):
    url: str = os.getenv('BASE_IMAGE_TAGS_URL', 'https://github.com/QCDIS/NaaVRE-flavors/releases/latest/download/base_image_tags.json')
    logger.debug(f'Base image tags URL: {url}')
    try:
        response = session.get(url)
        response.raise_for_status()
        dat: dict[str, dict[str, str]] = response.json()
    except (requests.ConnectionError, requests.HTTPError, requests.JSONDecodeError,) as e:
        msg: str = f'Error loading base image tags from {url}\n{e}'
        logger.debug(msg)
        return Response({'error': msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    Origin: str | None = request.headers.get('Origin', '*')
    return Response(dat, headers={'Access-Control-Allow-Origin': Origin})
