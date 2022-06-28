from dataclasses import fields
from rest_framework import serializers
from . import models


class CellSerializer(serializers.ModelSerializer):

    class Meta:

        model = models.Cell
        fields = "__all__"