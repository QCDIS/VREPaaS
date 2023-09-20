from sys import stdout
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from . import serializers
from . import models
from workflows.models import Workflow
from workflows.serializers import WorkflowSerializer
import requests
from vreapis.views import GetSerializerMixin


class VirtualLabViewSet(GetSerializerMixin, viewsets.ModelViewSet):

    lookup_field = "slug"
    queryset = models.VirtualLab.objects.all()
    serializer_class = serializers.VirtualLabDetailSerializer
    serializer_action_classes = {
        'list': serializers.VirtualLabSerializer
    }


class VirtualLabInstanceViewSet(
        GetSerializerMixin,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet,
        ):

    model = models.VirtualLabInstance
    queryset = model.objects.all()
    serializer_class = serializers.VirtualLabInstanceSerializer

    def get_queryset(self):
        vlab_slug = self.request.query_params.get('vlab_slug', None)
        if vlab_slug:
            return self.model.objects.filter(vlab__slug=vlab_slug)
        else:
            return self.model.objects.all()
