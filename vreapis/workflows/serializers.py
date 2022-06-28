from .models import Workflow
from rest_framework import serializers

class WorkflowListSerializer(serializers.ListSerializer):

    def update(self, instances, validated_data):
        
        instance_hash = {index: instance for index, instance in enumerate(instances)}

        result = [
            self.child.update(instance_hash[index], attrs)
            for index, attrs in enumerate(validated_data)
        ]

        return result


class WorkflowSerializer(serializers.ModelSerializer):

    argo_id = serializers.CharField()

    class Meta:
        model = Workflow
        fields = "__all__"
        list_serializer_class = WorkflowListSerializer

