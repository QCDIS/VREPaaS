from sys import stdout
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
import requests as rqs
from . import serializers
from . import models


class GetSerializerMixin(object):

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()


class VirtualLabViewSet(GetSerializerMixin, viewsets.ModelViewSet):

    queryset = models.VirtualLab.objects.all()
    serializer_class = serializers.VirtualLabDetailSerializer
    serializer_action_classes = {
        'list': serializers.VirtualLabSerializer
    }


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

    @action(detail=False, methods=['POST'], name='Submit a workflow')
    def submit(self, request, *args, **kwargs):

        ARGO_URL = 'https://lfw-ds001-i022.lifewatch.dev:32443/ess-22-argowf/api/v1/workflows/ess-22'
        workflow = request.data

        print(request.data)

        resp = rqs.post(
            ARGO_URL,
            json = workflow,
            headers = {
                'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjRqWGNWSVoyelFMRV9TenZ3a19vYUVvR0pYTkxpdS1CWjlXVHA0RnFQdmcifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im5hYXZyZWFwaTItdG9rZW4tZ3JnZmQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoibmFhdnJlYXBpMiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImFmMzFkYWNiLWMxYWMtNDJkYy1hYTAwLTM0ZDY0NGVkNjRiNiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0Om5hYXZyZWFwaTIifQ.VWngM11PLYjhUzHPFGQA-fb5JqJjQcNtheIfuDcAHHP0A_rlbQtbWeUPTN_j6mEIm0VTU990-a3hl8LDZeS7iGQknT73TJi8W836zCD6xmJYL9Dnk6JjTfDcLKft7u4auW2_cimdKM60P9psOJyLGGRLYS7tFzXyoEJGPboUrlnmVT03lrzqEUl6Ni1oH0S56HIJBJ89O2GeKhakayKbgesWr3EjELdawbAIBw8pmQE0R0dftddO1tdUXCph_HJkFuiRvt8RqYJiKFL7KogsmwhnSsRlzqncIKAPmKhamtW09E4sNc_Q60QQGmAVmVpaPkCP1jNpY_PRuQMZQmY57g'
            }
        )
        
        return Response(resp)
