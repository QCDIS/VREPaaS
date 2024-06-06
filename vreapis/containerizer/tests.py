import glob
import os
import json
import uuid

from django.test import TestCase, Client
from django.conf import settings
from django.contrib.auth.models import User
from urllib.parse import urlencode
import requests
import nbformat
from slugify import slugify
from unittest import mock

from services.extractor.pyextractor import PyExtractor
from services.extractor.rextractor import RExtractor
from services.converter import ConverterReactFlowChart
from db.cell import Cell
from .views import ExtractorHandler

base_path = ''
if os.path.exists('resources'):
    base_path = 'resources'
elif os.path.exists('tests/resources/'):
    base_path = 'tests/resources/'


def get_auth_header() -> dict[str, str]:
    return {'Authorization': f'Token {settings.NAAVRE_API_TOKEN}'}


class ContainerizerTestCase(TestCase):
    @staticmethod
    def Keycloak_login() -> dict[str, any]:
        return requests.post(settings.KEYCLOAK_LOGIN_URL, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=urlencode({'client_id': 'myclient', 'grant_type': 'password', 'scope': 'openid', 'username': 'u', 'password': 'u'}), verify=settings.ALLOW_INSECURE_TLS).json()

    def test_get_base_images(self):
        client = Client()
        dummy_username = f'test'
        dummy_password = '0'
        try:
            dummy_user: User = User.objects.get(username=dummy_username)
        except User.DoesNotExist:
            dummy_user = User.objects.create_user(dummy_username, password=dummy_password)
        client.login(username=dummy_username, password=dummy_password)

        response = client.get('/api/containerizer/baseimagetags/', headers=get_auth_header())
        self.assertEqual(response.status_code, 200)
        images = response.json()
        self.assertIsInstance(images, dict)
        self.assertGreater(len(images), 0)


class ExtractorTestCase(TestCase):
    # Reference parameter values for `test_param_values_*.json`
    param_values_ref = {
        'param_float': '1.1',
        'param_int': '1',
        'param_list': '[1, 2, 3]',
        'param_string': 'param_string value',
        'param_string_with_comment': 'param_string value',
    }

    def setUp(self):  # use setUp instead of __init__, or 'uncaught TypeError: __init__() takes 1 positional argument but 2 were given'
        super().__init__()

    def create_cell(self, payload_path=None):
        with open(payload_path, 'r') as file:
            payload = json.load(file)

        cell_index = payload['cell_index']
        notebook = nbformat.reads(json.dumps(payload['notebook']), nbformat.NO_CONVERT)
        source = notebook.cells[cell_index].source
        if payload['kernel'] == "IRkernel":
            extractor = RExtractor(notebook, source)
        else:
            extractor = PyExtractor(notebook, source)

        title = source.partition('\n')[0]
        title = slugify(title) if title and title[
            0] == "#" else "Untitled"

        if 'JUPYTERHUB_USER' in os.environ:
            title += '-' + slugify(os.environ['JUPYTERHUB_USER'])

        ins = {}
        outs = {}
        params = {}
        confs = []
        dependencies = []

        # Check if cell is code. If cell is for example markdown we get execution from 'extractor.infere_cell_inputs(source)'
        if notebook.cells[cell_index].cell_type == 'code':
            ins = extractor.infer_cell_inputs()
            outs = extractor.infer_cell_outputs()

            confs = extractor.extract_cell_conf_ref()
            dependencies = extractor.infer_cell_dependencies(confs)

        node_id = str(uuid.uuid4())[:7]
        cell = Cell(
            node_id=node_id,
            title=title,
            task_name=slugify(title.lower()),
            original_source=source,
            inputs=ins,
            outputs=outs,
            params=params,
            confs=confs,
            dependencies=dependencies,
            container_source=""
        )
        if notebook.cells[cell_index].cell_type == 'code':
            cell.integrate_configuration()
            params = extractor.extract_cell_params(cell.original_source)
            cell.add_params(params)
            cell.add_param_values(params)

        return cell

    def extract_cell(self, payload_path):
        # Check if file exists
        if os.path.exists(payload_path):
            cell = self.create_cell(payload_path)

            node = ConverterReactFlowChart.get_node(cell.node_id, cell.title, cell.inputs, cell.outputs, cell.params, )

            chart = {'offset': {'x': 0, 'y': 0, }, 'scale': 1, 'nodes': {cell.node_id: node}, 'links': {}, 'selected': {}, 'hovered': {}, }

            cell.chart_obj = chart
            return cell.toJSON()
        return None

    def test_extract_cell(self):
        notebooks_json_path = os.path.join(base_path, 'notebooks')
        notebooks_files = glob.glob(
            os.path.join(notebooks_json_path, "*.json")
        )
        for notebook_file in notebooks_files:
            cell = self.extract_cell(notebook_file)
            if cell:
                cell = json.loads(cell)
                for conf_name in (cell['confs']):
                    self.assertFalse('conf_' in cell['confs'][conf_name].split('=')[1], 'conf_ values should not contain conf_ prefix in ''assignment')
                # All params should have matching values
                for param_name in cell['params']:
                    self.assertTrue(param_name in cell['param_values'])

                # For notebook_file test_param_values_*.json, extracted params should match with self.param_values_ref
                if os.path.basename(notebook_file) in ['test_param_values_Python.json', 'test_param_values_R.json', ]:
                    for param_name in cell['params']:
                        self.assertTrue(cell['param_values'][param_name] == self.param_values_ref[param_name])


class ExtractorHandlerTestCase(TestCase):
    def test(self):
        notebooks_json_path = os.path.join(base_path, 'notebooks')
        notebooks_files = glob.glob(os.path.join(notebooks_json_path, "*.json"))
        for notebook_file in notebooks_files:
            with open(notebook_file, 'r') as file:
                notebook = json.load(file)
                # print(f'[Notebook File]{os.linesep}{notebook_file}')
                # print(f'[Notebook Content]{os.linesep}{notebook}')
            file.close()
            client = Client()
            response = client.post('/api/containerizer/extractorhandler/', headers=get_auth_header(), data=notebook, content_type="application/json")
            self.assertEqual(response.status_code, 200)
            # get JSON response
            JSON_response = json.loads(response.data)
            self.assertIsNotNone(JSON_response)
            cell = notebook['notebook']['cells'][notebook['cell_index']]
            print('cell: ', cell)
