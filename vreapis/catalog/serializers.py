from rest_framework.serializers import ModelSerializer
from . import models


class CellSerializer(ModelSerializer):
    class Meta:
        model = models.Cell
        fields = '__all__'
