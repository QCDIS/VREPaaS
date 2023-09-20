from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_gis import filters

from vreapis.views import GetSerializerMixin

from . import models
from . import serializers


class DataProductsViewSet(
        GetSerializerMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet,
        ):
    model = models.DataProduct
    queryset = model.objects.all()
    serializer_class = serializers.DataProductSerializer
    serializer_action_classes = {
        'list': serializers.DataProductSerializer,
        }

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = []
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        print(request.data)
        return super().create(request)

    def get_queryset(self):
        vlab_slug = self.request.query_params.get('vlab_slug', None)
        if vlab_slug:
            return self.model.objects.filter(vlab__slug=vlab_slug)
        else:
            return self.model.objects.all()



class GeoDataProductsViewSet(DataProductsViewSet):
    model = models.GeoDataProduct
    queryset = model.objects.all()
    serializer_class = serializers.GeoDataProductSerializer
    serializer_action_classes = {
        'list': serializers.GeoDataProductSerializer,
        }
    bbox_filter_field = 'spatial_coverage'
    bbox_filter_include_overlapping = True
    filter_backends = (filters.InBBoxFilter,)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = []
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
