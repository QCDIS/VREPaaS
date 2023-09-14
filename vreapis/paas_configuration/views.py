from rest_framework import viewsets
from vreapis.views import GetSerializerMixin

from .models import PaasConfiguration
from .serializers import PaasConfigurationSerializer


class PaasConfigurationViewSet(GetSerializerMixin, viewsets.ModelViewSet):

    http_method_names = ['get']

    queryset = PaasConfiguration.objects.all()
    serializer_class = PaasConfigurationSerializer
    serializer_action_classes = {
        'list': PaasConfigurationSerializer
        }
