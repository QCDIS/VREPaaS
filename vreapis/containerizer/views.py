import os
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
import requests
import common


@api_view(['GET'])
def get_base_images(request):
    url: str = os.getenv('BASE_IMAGE_TAGS_URL', 'https://github.com/QCDIS/NaaVRE-flavors/releases/latest/download/base_image_tags.json')
    common.logger.debug(f'Base image tags URL: {url}')
    try:
        response = common.session.get(url)
        response.raise_for_status()
        dat: dict[str, dict[str, str]] = response.json()
    except (requests.ConnectionError, requests.HTTPError, requests.JSONDecodeError,) as e:
        msg: str = f'Error loading base image tags from {url}\n{e}'
        common.logger.debug(msg)
        return Response({'error': msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    Origin: str = request.headers.get('Origin', '*')
    return Response(dat, headers={'Access-Control-Allow-Origin': Origin})
