from sys import stdout
from rest_framework import viewsets
from rest_framework.decorators import action
from . import serializers
from . import models
from workflows.models import Workflow
from workflows.serializers import WorkflowSerializer
import requests
from vreapis.views import GetSerializerMixin
from rest_framework.response import Response

class AssignmentViewSet(GetSerializerMixin, viewsets.ModelViewSet):

    lookup_field = "slug"
    queryset = models.Assignment.objects.all()
    serializer_class = serializers.AssignmentDetailSerializer
    serializer_action_classes = {
        'list': serializers.AssignmentSerializer
    }

class UploadViewSet(GetSerializerMixin, viewsets.ModelViewSet):
    serializer_class = serializers.FileSerializer
    queryset = models.File.objects.all()
    serializer_class = serializers.FileSerializer

