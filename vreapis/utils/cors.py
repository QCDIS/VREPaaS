import django.http
import rest_framework.request


def get_CORS_headers(request: django.http.HttpRequest | rest_framework.request.Request) -> dict[str, str]:
    Origin: str = request.META.get('HTTP_ORIGIN')
    return {'Access-Control-Allow-Origin': Origin}
