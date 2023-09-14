from rest_framework import serializers
from .models import PaasConfiguration


class PaasConfigurationSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaasConfiguration
        fields = (
            'title',
            'description',
            'documentation_url',
            )
