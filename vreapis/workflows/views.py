from email.policy import HTTP
import io

import requests
from rest_framework import mixins, viewsets, status
from rest_framework.parsers import JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response
from vreapis.views import GetSerializerMixin
from . import serializers
from virtual_labs.models import VirtualLab
from virtual_labs.serializers import VirtualLabDetailSerializer
import logging
from . import models, serializers

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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

    def get_queryset(self):

        query_params = self.request.query_params
        vlab_slug = query_params.get('vlab_slug', None)
        vlab_query_set = VirtualLab.objects.filter(slug=vlab_slug)

        if vlab_slug:
            if vlab_query_set.exists():
                vlab = vlab_query_set.get()
                return models.Workflow.objects.filter(vlab=vlab.id)

        else:
            return models.Workflow.objects.all()

    def list(self, request, *args, **kwargs):

        query_params = self.request.query_params
        vlab_slug = query_params.get('vlab_slug', None)

        if vlab_slug:
            ARGO_URL = f"https://lfw-ds001-i022.lifewatch.dev:32443/ess-22-argowf/api/v1/workflows/ess-22?listOptions.labelSelector=vlab_slug={vlab_slug}"
        else:
            ARGO_URL = f"https://lfw-ds001-i022.lifewatch.dev:32443/ess-22-argowf/api/v1/workflows/ess-22"

        resp_list = requests.get(
            ARGO_URL,
            headers={
                'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjRqWGNWSVoyelFMRV9TenZ3a19vYUVvR0pYTkxpdS1CWjlXVHA0RnFQdmcifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im5hYXZyZWFwaTItdG9rZW4tZ3JnZmQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoibmFhdnJlYXBpMiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImFmMzFkYWNiLWMxYWMtNDJkYy1hYTAwLTM0ZDY0NGVkNjRiNiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0Om5hYXZyZWFwaTIifQ.VWngM11PLYjhUzHPFGQA-fb5JqJjQcNtheIfuDcAHHP0A_rlbQtbWeUPTN_j6mEIm0VTU990-a3hl8LDZeS7iGQknT73TJi8W836zCD6xmJYL9Dnk6JjTfDcLKft7u4auW2_cimdKM60P9psOJyLGGRLYS7tFzXyoEJGPboUrlnmVT03lrzqEUl6Ni1oH0S56HIJBJ89O2GeKhakayKbgesWr3EjELdawbAIBw8pmQE0R0dftddO1tdUXCph_HJkFuiRvt8RqYJiKFL7KogsmwhnSsRlzqncIKAPmKhamtW09E4sNc_Q60QQGmAVmVpaPkCP1jNpY_PRuQMZQmY57g'
            }
        )

        resp_list_data = resp_list.json()

        if resp_list_data['items']:

            items = resp_list_data['items']
            instances = self.get_queryset()

            data_items = [
                {
                    'argo_id': item['metadata']['name'],
                    'status': item['status']['phase'],
                    'progress': item['status']['progress']
                }
                for item in items
            ]

            wf_serializer = serializers.WorkflowSerializer(instances, data=data_items, partial=True, many=True)

            if wf_serializer.is_valid(raise_exception=True):
                print("Serializer is valid")
                wf_serializer.save()

        return super().list(self, request, *args, **kwargs)

    @action(detail=False, methods=['POST'], name='Submit a workflow')
    def submit(self, request, *args, **kwargs):

        ARGO_API_URL = 'https://lfw-ds001-i022.lifewatch.dev:32443/ess-22-argowf/api/v1/workflows/ess-22'
        ARGO_URL = 'https://lfw-ds001-i022.lifewatch.dev:32443/ess-22-argowf/workflows/ess-22'

        if 'workflow_payload' not in request.data:
            logger.error('Request did not contain workflow payload')
            return Response('Request did not contain workflow payload', status=status.HTTP_400_BAD_REQUEST)

        workflow = request.data['workflow_payload']
        if 'vlab' not in request.data:
            logger.error('Request did not contain vlab info')
            return Response('Request did not contain vlab info', status=status.HTTP_400_BAD_REQUEST)
        vlab_slug = request.data['vlab']

        try:
            resp_submit = requests.post(
                ARGO_API_URL,
                json=workflow,
                headers={
                    'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjRqWGNWSVoyelFMRV9TenZ3a19vYUVvR0pYTkxpdS1CWjlXVHA0RnFQdmcifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im5hYXZyZWFwaTItdG9rZW4tZ3JnZmQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoibmFhdnJlYXBpMiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImFmMzFkYWNiLWMxYWMtNDJkYy1hYTAwLTM0ZDY0NGVkNjRiNiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0Om5hYXZyZWFwaTIifQ.VWngM11PLYjhUzHPFGQA-fb5JqJjQcNtheIfuDcAHHP0A_rlbQtbWeUPTN_j6mEIm0VTU990-a3hl8LDZeS7iGQknT73TJi8W836zCD6xmJYL9Dnk6JjTfDcLKft7u4auW2_cimdKM60P9psOJyLGGRLYS7tFzXyoEJGPboUrlnmVT03lrzqEUl6Ni1oH0S56HIJBJ89O2GeKhakayKbgesWr3EjELdawbAIBw8pmQE0R0dftddO1tdUXCph_HJkFuiRvt8RqYJiKFL7KogsmwhnSsRlzqncIKAPmKhamtW09E4sNc_Q60QQGmAVmVpaPkCP1jNpY_PRuQMZQmY57g'
                }
            )
        except Exception as ex:
            logger.error(str(ex))
            return Response('Error while submitting workflow in: '+ARGO_API_URL, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        resp_submit_data = resp_submit.json()
        resp_detail = requests.get(
            f"{ARGO_API_URL}/{resp_submit_data['metadata']['name']}",
            json=workflow,
            headers={
                'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjRqWGNWSVoyelFMRV9TenZ3a19vYUVvR0pYTkxpdS1CWjlXVHA0RnFQdmcifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im5hYXZyZWFwaTItdG9rZW4tZ3JnZmQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoibmFhdnJlYXBpMiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImFmMzFkYWNiLWMxYWMtNDJkYy1hYTAwLTM0ZDY0NGVkNjRiNiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0Om5hYXZyZWFwaTIifQ.VWngM11PLYjhUzHPFGQA-fb5JqJjQcNtheIfuDcAHHP0A_rlbQtbWeUPTN_j6mEIm0VTU990-a3hl8LDZeS7iGQknT73TJi8W836zCD6xmJYL9Dnk6JjTfDcLKft7u4auW2_cimdKM60P9psOJyLGGRLYS7tFzXyoEJGPboUrlnmVT03lrzqEUl6Ni1oH0S56HIJBJ89O2GeKhakayKbgesWr3EjELdawbAIBw8pmQE0R0dftddO1tdUXCph_HJkFuiRvt8RqYJiKFL7KogsmwhnSsRlzqncIKAPmKhamtW09E4sNc_Q60QQGmAVmVpaPkCP1jNpY_PRuQMZQmY57g'
            }
        )

        resp_detail_data = resp_detail.json()
        VirtualLab.objects
        try:
            logger.info('Querying vlab: ' + vlab_slug)
            vlab = VirtualLab.objects.get(slug=vlab_slug)
        except Exception as ex:
            logger.error(str(ex))
            return Response('Error while getting vlab: '+vlab_slug, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not vlab:
            logger.error('vlab: '+vlab_slug+ ' not found')
            return Response('vlab: '+vlab_slug+ ' not found', status=status.HTTP_404_NOT_FOUND)

        new_data = {'argo_id': resp_submit_data['metadata']['name'],
                    'status': f"{resp_detail_data['status']['phase']} - {resp_detail_data['status']['progress']}",
                    'vlab': vlab.id, 'argo_url': f"{ARGO_URL}/{resp_detail_data['metadata']['name']}"}

        new_workflow = serializers.WorkflowSerializer(data=new_data)

        if new_workflow.is_valid(raise_exception=True):
            new_workflow.save()

        return Response(new_workflow.data)
