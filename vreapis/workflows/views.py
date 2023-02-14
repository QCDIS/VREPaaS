import os
from email.policy import HTTP
import io

import requests
from rest_framework import mixins, viewsets
from rest_framework.parsers import JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response
from vreapis.views import GetSerializerMixin
from . import serializers
from virtual_labs.models import VirtualLab
from virtual_labs.serializers import VirtualLabDetailSerializer

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
            ARGO_URL = os.getenv('ARGO_URL') + '?listOptions.labelSelector=vlab_slug=' + vlab_slug
        else:
            ARGO_URL = os.getenv('ARGO_URL')

        resp_list = requests.get(
            ARGO_URL,
            headers={
                'Authorization': os.getenv('ARGO_API_TOKEN')
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

        ARGO_API_URL = os.getenv('ARGO_URL')+'/api/v1/workflows/ess-22'
        ARGO_URL = os.getenv('ARGO_URL')+'/workflows/ess-22'

        workflow = request.data['workflow_payload']
        vlab_slug = request.data['vlab']

        resp_submit = requests.post(
            ARGO_API_URL,
            json=workflow,
            headers={
                'Authorization': os.getenv('ARGO_API_TOKEN')
            }
        )

        resp_submit_data = resp_submit.json()

        resp_detail = requests.get(
            f"{ARGO_API_URL}/{resp_submit_data['metadata']['name']}",
            json=workflow,
            headers={
                'Authorization': os.getenv('ARGO_API_TOKEN')
            }
        )

        resp_detail_data = resp_detail.json()

        vlab = VirtualLab.objects.get(slug=vlab_slug)
        new_data = {'argo_id': resp_submit_data['metadata']['name'],
                    'status': f"{resp_detail_data['status']['phase']} - {resp_detail_data['status']['progress']}",
                    'vlab': vlab.id, 'argo_url': f"{ARGO_URL}/{resp_detail_data['metadata']['name']}"}

        new_workflow = serializers.WorkflowSerializer(data=new_data)

        if new_workflow.is_valid(raise_exception=True):
            new_workflow.save()

        return Response(new_workflow.data)
