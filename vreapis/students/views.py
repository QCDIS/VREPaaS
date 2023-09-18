from sys import stdout
from rest_framework import viewsets
from rest_framework.decorators import action
from . import serializers
from . import models
import requests
from vreapis.views import GetSerializerMixin

import logging
logger = logging.getLogger(__name__)


class StudentViewSet(GetSerializerMixin, viewsets.ModelViewSet):

    lookup_field = "slug"
    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer
    serializer_action_classes = {
        'list': serializers.StudentSerializer
    }
