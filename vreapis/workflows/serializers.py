from unittest import result
from .models import Workflow
from rest_framework import serializers


class WorkflowListSerializer(serializers.ListSerializer):

    def save(self, **kwargs):
        print("Calling save")
        return super().save(**kwargs)

    def update(self, instances, validated_data):

        print("List update called")

        wf_mapping = {wf.argo_id: wf for wf in instances}
        data_mapping = {item['argo_id']: item for item in validated_data}

        # Perform creations and updates.
        ret = []
        for argo_id, data in data_mapping.items():
            workflow = wf_mapping.get(argo_id, None)
            if workflow is not None:
                ret.append(self.child.update(workflow, data))

        # Perform deletions.
        for argo_id, workflow in wf_mapping.items():
            if argo_id not in data_mapping:
                workflow.delete()

        return ret


class WorkflowSerializer(serializers.ModelSerializer):
    argo_id = serializers.CharField()

    class Meta:
        model = Workflow
        fields = "__all__"
        list_serializer_class = WorkflowListSerializer
