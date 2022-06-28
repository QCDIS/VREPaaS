from sys import stdout
from rest_framework import viewsets
from . import serializers
from . import models
from vreapis.views import GetSerializerMixin


class VirtualLabViewSet(GetSerializerMixin, viewsets.ModelViewSet):

    queryset = models.VirtualLab.objects.all()
    serializer_class = serializers.VirtualLabDetailSerializer
    serializer_action_classes = {
        'list': serializers.VirtualLabSerializer
    }

