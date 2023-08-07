from sys import stdout
from rest_framework import viewsets
from rest_framework.decorators import action
from . import serializers
from . import models
from workflows.models import Workflow
from workflows.serializers import WorkflowSerializer
import requests
from vreapis.views import GetSerializerMixin


class AssignmentViewSet(GetSerializerMixin, viewsets.ModelViewSet):

    lookup_field = "slug"
    queryset = models.VirtualLab.objects.all()
    serializer_class = serializers.VirtualLabDetailSerializer
    serializer_action_classes = {
        'list': serializers.AssignmentsSerializer
    }


