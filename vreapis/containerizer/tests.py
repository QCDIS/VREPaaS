import datetime
import glob
import os
import json
import shlex
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from django.test import TestCase, Client
from django.conf import settings
from django.contrib.auth.models import User
from urllib.parse import urlencode
import requests
import nbformat
from github import Github
from slugify import slugify
from tornado.gen import sleep

import common
from db.catalog import Catalog
from services.extractor.pyextractor import PyExtractor
from services.extractor.rextractor import RExtractor
from services.converter import ConverterReactFlowChart
from db.cell import Cell

base_path = ''
if os.path.exists('resources'):
    base_path = 'resources'
elif os.path.exists('tests/resources/'):
    base_path = 'tests/resources/'


def get_auth_header() -> dict[str, str]:
    return {'Authorization': f'Token {settings.NAAVRE_API_TOKEN}'}


class GetBaseImagesTestCase(TestCase):
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
        notebooks_files = glob.glob(os.path.join(notebooks_json_path, "*.json"))
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
            file.close()
            client = Client()
            response = client.post('/api/containerizer/extractorhandler/', headers=get_auth_header(), data=notebook, content_type="application/json")
            self.assertEqual(response.status_code, 200)
            # get JSON response
            JSON_response = json.loads(response.data)
            self.assertIsNotNone(JSON_response)
            cell = notebook['notebook']['cells'][notebook['cell_index']]
            print('cell: ', cell)


class CellsHandlerTestCase(TestCase):
    cells_path = os.path.join(str(Path.home()), 'NaaVRE', 'cells')
    github_url_repos = 'https://api.github.com/repos'

    def setUp(self):
        self.client = Client()

    def create_cell_and_add_to_cat(self, cell_path=None):
        print('Creating cell from: ', cell_path)
        with open(cell_path, 'r') as file:
            cell = json.load(file)
        file.close()
        notebook_dict = {}
        if 'notebook_dict' in cell:
            notebook_dict = cell['notebook_dict']
        test_cell = Cell(cell['title'], cell['task_name'], cell['original_source'], cell['inputs'],
                         cell['outputs'],
                         cell['params'], cell['confs'], cell['dependencies'], cell['container_source'],
                         cell['chart_obj'], cell['node_id'], cell['kernel'], notebook_dict)
        test_cell.types = cell['types']
        test_cell.base_image = cell['base_image']
        Catalog.editor_buffer = test_cell
        return test_cell, cell

    def call_cell_handler(self):
        return self.client.post('/api/containerizer/cellshandler/', content_type='application/json', headers=get_auth_header())

    def delete_text(self, file_path, text_to_delete):
        # Read the file
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Remove the text from each line
        updated_lines = []
        for line in lines:
            updated_line = line.replace(text_to_delete, '')
            updated_lines.append(updated_line)

        # Write the updated lines to the file
        with open(file_path, 'w') as file:
            file.writelines(updated_lines)

    def wait_for_github_api_resources(self):
        github = Github(Catalog.get_repositories()[0]['token'])
        rate_limit = github.get_rate_limit()
        while rate_limit.core.remaining <= 0:
            reset = rate_limit.core.reset
            # Calculate remaining time for reset
            remaining_time = reset.timestamp() - datetime.datetime.now().timestamp()
            common.logger.debug(f'Remaining time for reset: {remaining_time} s')
            common.logger.debug(f'API rate exceeded, waiting')
            common.logger.debug(f'Sleeping for: {remaining_time + 1}')
            sleep(remaining_time + 1)
            rate_limit = github.get_rate_limit()

    def get_github_workflow_runs(self, owner=None, repository_name=None, t_utc=None, token=None):
        workflow_runs_url = CellsHandlerTestCase.github_url_repos + '/' + owner + '/' + repository_name + '/actions/runs'
        if t_utc:
            t_start = (t_utc - datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            t_stop = (t_utc + datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            workflow_runs_url += f"?created={t_start}..{t_stop}"
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        workflow_runs = common.session.get(url=workflow_runs_url, verify=False, headers=headers)
        if workflow_runs.status_code != 200:
            return None
        workflow_runs_json = json.loads(workflow_runs.text)
        return workflow_runs_json

    def get_github_workflow_jobs(self, jobs_url=None, token=None):
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        jobs = common.session.get(url=jobs_url, verify=False, headers=headers)
        if jobs.status_code == 200:
            return json.loads(jobs.text)
        else:
            raise Exception('Error getting jobs for workflow run: ' + jobs.text)

    def find_job(self,
                 wf_id=None,
                 wf_creation_utc=None,
                 owner=None,
                 repository_name=None,
                 token=None,
                 job_id=None,
                 ):
        f""" Find Github workflow job

        If job_id is set, retrieve it through
        https://api.github.com/repos/{owner}/{repository_name}/actions/jobs/{job_id}

        Else, get all workflows runs created around wf_creation_utc through
        https://api.github.com/repos/{owner}/{repository_name}/actions/runs
        and find the one matching {wf_id}
        """
        if job_id:
            jobs_url = CellsHandlerTestCase.github_url_repos + '/' + owner + '/' + repository_name + '/actions/jobs/' + str(job_id)
            self.wait_for_github_api_resources()
            job = self.get_github_workflow_jobs(jobs_url, token=token)
            return job
        self.wait_for_github_api_resources()
        runs = self.get_github_workflow_runs(
            owner=owner,
            repository_name=repository_name,
            t_utc=wf_creation_utc,
            token=token)
        if not runs:
            return None
        for run in runs['workflow_runs']:
            jobs_url = run['jobs_url']
            self.wait_for_github_api_resources()
            jobs = self.get_github_workflow_jobs(jobs_url, token=token)
            for job in jobs['jobs']:
                if job['name'] == wf_id:
                    job['head_sha'] = run['head_sha']
                    return job
        return None

    def wait_for_job(self,
                     wf_id=None,
                     wf_creation_utc=None,
                     owner=None,
                     repository_name=None,
                     token=None,
                     job_id=None,
                     timeout=200,
                     wait_for_completion=False,
                     ):
        """ Call find_job until something is returned or timeout is reached

        :param wf_id: passed to find_job
        :param wf_creation_utc: passed to find_job
        :param owner: passed to find_job
        :param repository_name: passed to find_job
        :param token: passed to find_job
        :param job_id: passed to find_job
        :param timeout: timeout in seconds
        :param wait_for_completion: wait for the job's status to be 'complete'

        :return: job or None
        """
        start_time = datetime.datetime.now().timestamp()  # seconds
        stop_time = start_time + timeout
        while datetime.datetime.now().timestamp() < stop_time:
            job = self.find_job(
                wf_id=wf_id,
                wf_creation_utc=wf_creation_utc,
                owner=owner,
                repository_name=repository_name,
                token=token,
                job_id=job_id,
            )
            if job:
                if not wait_for_completion:
                    return job
                if wait_for_completion and (job['status'] == 'completed'):
                    return job
            sleep(5)

    def test(self):
        cells_json_path = os.path.join(base_path, 'cells')
        cells_files = os.listdir(cells_json_path)
        test_cells = []
        for cell_file in cells_files:
            cell_path = os.path.join(cells_json_path, cell_file)
            test_cell, cell = self.create_cell_and_add_to_cat(cell_path=cell_path)
            response = self.call_cell_handler()
            self.assertEqual(200, response.status_code)
            wf_id = response.data['wf_id']
            wf_creation_utc = datetime.datetime.now(tz=datetime.timezone.utc)
            dispatched_github_workflow = response.data['dispatched_github_workflow']
            test_cells.append({
                'wf_id': wf_id,
                'wf_creation_utc': wf_creation_utc,
                'dispatched_github_workflow': dispatched_github_workflow,
            })
            if 'skip_exec' in cell and cell['skip_exec']:
                continue
            if 'python' in test_cell.kernel and 'skip_exec':
                cell_path = os.path.join(CellsHandlerTestCase.cells_path, test_cell.task_name, 'task.py')
                print('---------------------------------------------------')
                print('Executing cell: ', cell_path)
                if 'example_inputs' in cell:
                    exec_args = [sys.executable, cell_path] + cell['example_inputs']
                else:
                    exec_args = [sys.executable, cell_path]

                cell_exec = subprocess.Popen(exec_args, stdout=subprocess.PIPE)
                text = cell_exec.communicate()[0]
                print(text)
                print("stdout:", cell_exec.stdout)
                print("stderr:", cell_exec.stderr)
                print("return code:", cell_exec.returncode)
                print('---------------------------------------------------')
                self.assertEqual(0, cell_exec.returncode, 'Cell execution failed: ' + cell_file)
            elif test_cell.kernel == 'IRkernel' and 'skip_exec':
                cell_path = os.path.join(CellsHandlerTestCase.cells_path, test_cell.task_name, 'task.R')
                run_local_cell_path = os.path.join(CellsHandlerTestCase.cells_path, test_cell.task_name, 'run_local.R')
                shutil.copy(cell_path, run_local_cell_path)
                self.delete_text(run_local_cell_path, 'setwd(\'/app\')')
                example_inputs = ''
                if 'example_inputs' in cell:
                    example_inputs = ' '.join(cell['example_inputs'])
                command = 'Rscript ' + run_local_cell_path + ' ' + example_inputs
                R_dependencies: list[str] = ['optparse', 'jsonlite', ]  # Some versions [e.g., older ones] may make this test fail
                for dependency in R_dependencies:
                    result = subprocess.run(['Rscript', '-e', f'if(!require("{dependency}")) install.packages("{dependency}")'], capture_output=True, text=True)
                    print(result.stdout)
                    print(result.stderr)
                    self.assertEqual(0, result.returncode, result.stderr)
                result = subprocess.run(shlex.split(command), capture_output=True, text=True)
                self.assertEqual(0, result.returncode, result.stderr)

        cat_repositories = Catalog.get_repositories()
        repo = cat_repositories[0]
        repo_token = repo['token']
        owner, repository_name = repo['url'].removeprefix('https://github.com/').split('/')
        if '.git' in repository_name:
            repository_name = repository_name.split('.git')[0]

        updated_cells = list(filter(
            lambda cell: cell['dispatched_github_workflow'],
            test_cells,
        ))

        for cell in updated_cells:
            # Get job id (many calls to the GitHub API)
            job = self.wait_for_job(
                wf_id=cell['wf_id'],
                wf_creation_utc=cell['wf_creation_utc'],
                owner=owner,
                repository_name=repository_name,
                token=repo_token,
                job_id=None,
                timeout=300,
                wait_for_completion=False,
            )
            cell['job'] = job

        for cell in updated_cells:
            # Wait for job completion (fewer calls)
            job = self.wait_for_job(
                wf_id=cell['wf_id'],
                wf_creation_utc=None,
                owner=owner,
                repository_name=repository_name,
                token=repo_token,
                job_id=cell['job']['id'],
                timeout=300,
                wait_for_completion=True,
            )
            cell['job'] = job

        for cell in updated_cells:
            self.assertIsNotNone(cell['job'], 'Job not found')
            self.assertEqual('completed', cell['job']['status'], 'Job not completed')
            self.assertEqual('success', cell['job']['conclusion'], 'Job not successful')
