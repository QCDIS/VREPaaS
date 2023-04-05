from rest_framework import mixins, viewsets
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
    queryset = models.DataProduct.objects.all()
    serializer_class = serializers.DataProductSerializer
    serializer_action_classes = {
        'list': serializers.DataProductSerializer,
        }

    def create(self, request, *args, **kwargs):
        print(request.data)
        return super().create(request)


class GeoDataProductsViewSet(
        GetSerializerMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet,
        ):
    queryset = models.GeoDataProduct.objects.all()
    serializer_class = serializers.GeoDataProductSerializer
    serializer_action_classes = {
        'list': serializers.GeoDataProductSerializer,
        }
    bbox_filter_field = 'spatial_coverage'
    bbox_filter_include_overlapping = True
    filter_backends = (filters.InBBoxFilter,)

    def create(self, request, *args, **kwargs):
        print(request.data)
        return super().create(request)
