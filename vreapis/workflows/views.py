import os

import requests
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from virtual_labs.models import VirtualLab
from vreapis.views import GetSerializerMixin
from . import models, serializers

argo_url = os.getenv('ARGO_URL')
argo_api_wf_url = argo_url+'/api/v1/workflows/'
argo_api_token = os.getenv('ARGO_API_TOKEN')
namespace = os.getenv('ARGO_NAMESPACE')

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
        print('----------------get_queryset-------------------------')
        query_params = self.request.query_params
        print('get_queryset query_params: ' + str(query_params))
        vlab_slug = query_params.get('vlab_slug', None)
        vlab_query_set = VirtualLab.objects.filter(slug=vlab_slug)

        if vlab_slug:
            if vlab_query_set.exists():
                vlab = vlab_query_set.get()
                return models.Workflow.objects.filter(vlab=vlab.id)

        else:
            return models.Workflow.objects.all()

    def list(self, request, *args, **kwargs):
        print('----------------list-------------------------')
        query_params = self.request.query_params
        print('list query_params: ' + str(query_params))
        vlab_slug = query_params.get('vlab_slug', None)
        if vlab_slug:
            call_url = argo_api_wf_url + '?listOptions.labelSelector=vlab_slug=' + vlab_slug
        else:
            call_url = argo_api_wf_url

        resp_list = requests.get(
            call_url,
            headers={
                'Authorization': argo_api_token
            }
        )
        print('------------------------------------------------------------------------')
        print('resp_list: ' + str(resp_list))

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
        print('----------------submit-------------------------')
        if not argo_api_wf_url:
            return Response({'message': 'Argo API URL not set'}, status=500)

        if argo_api_wf_url.endswith('/'):
            call_url = argo_api_wf_url+namespace
        else:
            call_url = argo_api_wf_url+'/'+namespace

        workflow = request.data['workflow_payload']
        vlab_slug = request.data['vlab']

        resp_submit = requests.post(
            call_url,
            json=workflow,
            headers={
                'Authorization': argo_api_token
            }
        )
        print(resp_submit.status_code)
        if resp_submit.status_code != 200:
            return Response({'message': 'Error in submitting workflow'}, status=resp_submit.status_code)
        resp_submit_data = resp_submit.json()

        resp_detail = requests.get(
            f"{call_url}/{resp_submit_data['metadata']['name']}",
            json=workflow,
            headers={
                'Authorization': argo_api_token
            }
        )
        if resp_detail.status_code != 200:
            return Response({'message': 'Error in getting workflow details'}, status=resp_detail.status_code)

        resp_detail_data = resp_detail.json()

        vlab = VirtualLab.objects.get(slug=vlab_slug)
        if not argo_url:
            return Response({'message': 'Argo URL not set'}, status=500)
        argo_exec_url = f"{argo_url}/workflows/{namespace}/{resp_detail_data['metadata']['name']}"
        new_data = {'argo_id': resp_submit_data['metadata']['name'],
                    'status': f"{resp_detail_data['status']['phase']} - {resp_detail_data['status']['progress']}",
                    'vlab': vlab.id, 'argo_url': argo_exec_url}

        new_workflow = serializers.WorkflowSerializer(data=new_data)

        if new_workflow.is_valid(raise_exception=True):
            new_workflow.save()

        return Response(new_workflow.data)
