from django.shortcuts import render
from requests import Response
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from vreapis.views import GetSerializerMixin

from . import models, serializers


class CellsViewSet(GetSerializerMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    queryset = models.Cell.objects.all()
    serializer_class = serializers.CellSerializer
    serializer_action_classes = {
        'list': serializers.CellSerializer
    }

    def create(self, request, *args, **kwargs):
        print(request.data)
        return super().create(request)
