import logging
import os

from django.conf import settings
import requests

from virtual_labs.models import VirtualLab

logger = logging.getLogger(__name__)


class ArgoAPI:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = os.environ['ARGO_API_TOKEN'].replace('"', '')

    def query(self, verb, path, **kwargs):
        url = self.base_url + path

        logger.debug(f'Calling Argo API: {verb} {url}')
        logger.debug(f'Options: {kwargs}')

        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers'].update({
            'Authorization': self.token,
            })

        resp = requests.request(
            verb,
            url=url,
            verify=(not settings.ALLOW_INSECURE_TLS),
            **kwargs,
            )

        logger.debug(f'Response: {resp.status_code} - {resp.text}')

        return resp

    def get(self, *args, **kwargs):
        return self.query('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.query('POST', *args, **kwargs)


class ArgoWorkflow:
    def __init__(self):
        self.url = os.environ['ARGO_URL']
        self.namespace = os.environ['ARGO_NAMESPACE']
        self.api = ArgoAPI(self.url + '/api/v1/workflows/' + self.namespace)

    def convert_argo_wf_to_paas(self, wf):
        """ Convert json description of argo workflow to serialized PaaS model

        :param wf: serialized argo workflow
        :returns: serialized PaaS workflow
        :raises: KeyError
        """
        vlab_slug = wf['metadata']['labels'].get('vlab_slug')
        try:
            vlab = VirtualLab.objects.get(slug=vlab_slug).id
        except VirtualLab.DoesNotExist:
            logger.error(f'Virtual Lab does not exist: {vlab_slug}')
            vlab = None
        return {
            'argo_id': wf['metadata']['name'],
            'created': wf['metadata']['creationTimestamp'],
            'status': wf['status'].get('phase'),
            'progress': wf['status'].get('progress'),
            'argo_url': os.path.join(self.url, 'workflows',
                                     self.namespace, wf['metadata']['name']),
            'vlab': vlab,
            }

    def list_workflows(self, vlab_slug=None):
        """ List workflows in argo

        :param vlab_slug: vlab slug
        :return: list of workflow properties, or None on errors
        """
        path = ''
        if vlab_slug:
            path += f'?listOptions.labelSelector=vlab_slug={vlab_slug}'
        resp = self.api.get(path)

        if resp.status_code != 200:
            logger.error(
                f'Error while getting workflows: '
                f'{resp.status_code} - {resp.text}'
                )
            return None

        resp_data = resp.json()

        try:
            items = resp_data['items']
        except KeyError:
            logger.error('No items')
            return None

        if items is None:
            # This is expected when there are no workflows in argo
            return []

        try:
            workflows = [self.convert_argo_wf_to_paas(item)
                         for item in items]
        except (KeyError, TypeError):
            logger.error(
                f'Could not convert workflows: {items}')
            return None

        return workflows

    def retrieve_workflow(self, wf_id):
        """ Retrieve properties of a single workflow

        :param wf_id: workflow id string
        :return: workflow properties, or None on errors
        """
        resp = self.api.get(f'/{wf_id}')

        if resp.status_code != 200:
            logger.error(
                f'Error while getting workflow: '
                f'{resp.status_code} - {resp.text}'
                )
            return None

        resp_data = resp.json()

        try:
            workflow = self.convert_argo_wf_to_paas(resp_data)
        except KeyError:
            logger.error(
                f'Could not convert workflow: {resp_data}')
            return None

        return workflow

    def submit_workflow(self, workflow):
        resp = self.api.post('', json=workflow)

        if resp.status_code != 200:
            logger.error(
                'Error while submitting workflow: '
                f'{resp.status_code} - {resp.text}'
                )
            try:
                resp_data = resp.json()
            except requests.exceptions.JSONDecodeError:
                resp_data = resp.text
            return None, resp_data

        resp_data = resp.json()

        try:
            workflow = self.convert_argo_wf_to_paas(resp_data)
        except KeyError:
            logger.error(
                f'Could not convert workflow: {resp_data}')
            return None, resp_data

        return workflow, resp_data
