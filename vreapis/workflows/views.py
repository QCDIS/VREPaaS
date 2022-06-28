from email.policy import HTTP
import io

import requests
from rest_framework import mixins, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response
from vreapis.views import GetSerializerMixin

from . import models, serializers


class WorkflowViewSet(GetSerializerMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):

    queryset = models.Workflow.objects.all()
    serializer_class = serializers.WorkflowSerializer
    serializer_action_classes = {
        'list': serializers.WorkflowSerializer
    }


    def list(self, request, *args, **kwargs):

        ARGO_URL = 'https://lfw-ds001-i022.lifewatch.dev:32443/ess-22-argowf/api/v1/workflows/ess-22'

        resp_list = requests.get(
            ARGO_URL,
            headers = {
                'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjRqWGNWSVoyelFMRV9TenZ3a19vYUVvR0pYTkxpdS1CWjlXVHA0RnFQdmcifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im5hYXZyZWFwaTItdG9rZW4tZ3JnZmQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoibmFhdnJlYXBpMiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImFmMzFkYWNiLWMxYWMtNDJkYy1hYTAwLTM0ZDY0NGVkNjRiNiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0Om5hYXZyZWFwaTIifQ.VWngM11PLYjhUzHPFGQA-fb5JqJjQcNtheIfuDcAHHP0A_rlbQtbWeUPTN_j6mEIm0VTU990-a3hl8LDZeS7iGQknT73TJi8W836zCD6xmJYL9Dnk6JjTfDcLKft7u4auW2_cimdKM60P9psOJyLGGRLYS7tFzXyoEJGPboUrlnmVT03lrzqEUl6Ni1oH0S56HIJBJ89O2GeKhakayKbgesWr3EjELdawbAIBw8pmQE0R0dftddO1tdUXCph_HJkFuiRvt8RqYJiKFL7KogsmwhnSsRlzqncIKAPmKhamtW09E4sNc_Q60QQGmAVmVpaPkCP1jNpY_PRuQMZQmY57g'
            }
        )

        resp_list_data = resp_list.json()
        items = resp_list_data['items']
        instances = models.Workflow.objects.all()

        data_items = [
            {
                'argo_id': item['metadata']['name'],
                'status': f"{item['status']['phase']} - {item['status']['progress']}"
            }
            for item in items
        ]

        wf_serializer = serializers.WorkflowSerializer(instances, data=data_items, many=True)

        if wf_serializer.is_valid(raise_exception=True):
            wf_serializer.save()

        return Response(data_items)


    @action(detail=False, methods=['POST'], name='Submit a workflow')
    def submit(self, request, *args, **kwargs):

        ARGO_URL = 'https://lfw-ds001-i022.lifewatch.dev:32443/ess-22-argowf/api/v1/workflows/ess-22'
        workflow = request.data

        resp_submit = requests.post(
            ARGO_URL,
            json = workflow,
            headers = {
                'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjRqWGNWSVoyelFMRV9TenZ3a19vYUVvR0pYTkxpdS1CWjlXVHA0RnFQdmcifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im5hYXZyZWFwaTItdG9rZW4tZ3JnZmQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoibmFhdnJlYXBpMiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImFmMzFkYWNiLWMxYWMtNDJkYy1hYTAwLTM0ZDY0NGVkNjRiNiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0Om5hYXZyZWFwaTIifQ.VWngM11PLYjhUzHPFGQA-fb5JqJjQcNtheIfuDcAHHP0A_rlbQtbWeUPTN_j6mEIm0VTU990-a3hl8LDZeS7iGQknT73TJi8W836zCD6xmJYL9Dnk6JjTfDcLKft7u4auW2_cimdKM60P9psOJyLGGRLYS7tFzXyoEJGPboUrlnmVT03lrzqEUl6Ni1oH0S56HIJBJ89O2GeKhakayKbgesWr3EjELdawbAIBw8pmQE0R0dftddO1tdUXCph_HJkFuiRvt8RqYJiKFL7KogsmwhnSsRlzqncIKAPmKhamtW09E4sNc_Q60QQGmAVmVpaPkCP1jNpY_PRuQMZQmY57g'
            }
        )

        resp_submit_data = resp_submit.json()

        resp_detail = requests.get(
            f"{ARGO_URL}/{resp_submit_data['metadata']['name']}",
            json = workflow,
            headers = {
                'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjRqWGNWSVoyelFMRV9TenZ3a19vYUVvR0pYTkxpdS1CWjlXVHA0RnFQdmcifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im5hYXZyZWFwaTItdG9rZW4tZ3JnZmQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoibmFhdnJlYXBpMiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImFmMzFkYWNiLWMxYWMtNDJkYy1hYTAwLTM0ZDY0NGVkNjRiNiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0Om5hYXZyZWFwaTIifQ.VWngM11PLYjhUzHPFGQA-fb5JqJjQcNtheIfuDcAHHP0A_rlbQtbWeUPTN_j6mEIm0VTU990-a3hl8LDZeS7iGQknT73TJi8W836zCD6xmJYL9Dnk6JjTfDcLKft7u4auW2_cimdKM60P9psOJyLGGRLYS7tFzXyoEJGPboUrlnmVT03lrzqEUl6Ni1oH0S56HIJBJ89O2GeKhakayKbgesWr3EjELdawbAIBw8pmQE0R0dftddO1tdUXCph_HJkFuiRvt8RqYJiKFL7KogsmwhnSsRlzqncIKAPmKhamtW09E4sNc_Q60QQGmAVmVpaPkCP1jNpY_PRuQMZQmY57g'
            }
        )

        resp_detail_data = resp_detail.json()

        new_data = {}

        new_data['argo_id'] = resp_submit_data['metadata']['name']
        new_data['status'] = f"{resp_detail_data['status']['phase']} - {resp_detail_data['status']['progress']}"
        new_data['vlab'] = 1

        new_workflow = serializers.WorkflowSerializer(data = new_data)

        if new_workflow.is_valid():
            new_workflow.save()

        return Response()
