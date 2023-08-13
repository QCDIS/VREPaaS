from rest_framework.serializers import ModelSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from . import models


class DataProductSerializer(ModelSerializer):
    class Meta:
        model = models.DataProduct
        fields = '__all__'


class GeoDataProductSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = models.GeoDataProduct
        fields = ('uuid', 'created', 'title', 'description', 'vlab',
                  'workflow', 'data_url', 'raster_data_url')
        geo_field = 'spatial_coverage'
