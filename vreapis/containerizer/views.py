import bisect
import importlib
import os
import json
import re
import sys
import copy
import time
import hashlib
import uuid
from typing import Optional
from pathlib import Path
import subprocess

import autopep8
from distro import distro
import jinja2
from django.db.models import QuerySet
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import viewsets
from rest_framework.request import Request
import requests
import nbformat
import jsonschema
from slugify import slugify
from github import Github, UnknownObjectException
from django.conf import settings

from catalog.serializers import CellSerializer
from containerizer.RContainerizer import RContainerizer
from db.repository import Repository
from services.extractor.extractor import DummyExtractor
from services.extractor.headerextractor import HeaderExtractor
from services.extractor.pyextractor import PyExtractor
from services.extractor.rextractor import RExtractor
from services.converter import ConverterReactFlowChart
import utils.cors
from auth.simple import StaticTokenAuthentication
from catalog.models import Cell

import common


def return_error(err_msg: str = 'Unknown ERROR', e: Optional[Exception] = None, stat: status = status.HTTP_400_BAD_REQUEST) -> Response:
    common.logger.error(err_msg, exc_info=e)
    return Response(err_msg, status=stat)


@api_view(['GET'])
@authentication_classes([StaticTokenAuthentication])
@permission_classes([IsAuthenticated])
def get_base_images(request):
    url: str = os.getenv('BASE_IMAGE_TAGS_URL', 'https://github.com/QCDIS/NaaVRE-flavors/releases/latest/download/base_image_tags.json')
    common.logger.debug(f'Base image tags URL: {url}')
    try:
        response = common.session.get(url)
        response.raise_for_status()
        dat: dict[str, dict[str, str]] = response.json()
    except (requests.ConnectionError, requests.HTTPError, requests.JSONDecodeError,) as e:
        return return_error(f'Error loading base image tags from {url}', e, stat=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(dat, headers=utils.cors.get_CORS_headers(request))


class ExtractorHandler(APIView):
    authentication_classes = [StaticTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def extract_cell_by_index(self, notebook: nbformat.notebooknode, cell_index: int) -> nbformat.NotebookNode:
        new_nb = copy.deepcopy(notebook)
        if cell_index < len(notebook.cells):
            new_nb.cells = [notebook.cells[cell_index]]
            return new_nb

    def set_notebook_kernel(self, notebook: nbformat.NotebookNode, kernel: str) -> nbformat.NotebookNode:
        new_nb: nbformat.NotebookNode = copy.deepcopy(notebook)
        # Replace kernel name in the notebook metadata
        new_nb.metadata['kernelspec'] = {
            'name': kernel,
            'display_name': kernel,
            'language': kernel,
        }
        return new_nb

    def get(self, request: Request):
        return return_error("Operation not supported.", stat=status.HTTP_400_BAD_REQUEST)

    def post(self, request: Request):
        payload = request.data
        # common.logger.debug('ExtractorHandler. payload: ' + json.dumps(payload, indent=4))
        if 'rmarkdown' in payload:
            # Directly setting `NotebookNode.metadata['jupytext'] = {'split_at_heading': True, }` has no use. I don't know why. So we don't use lib jupytext here.
            command_jupytext = f'source {settings.VENV_ACTIVATOR}; jupytext --from Rmd --to ipynb --opt split_at_heading=true -o -'
            process_jupytext = subprocess.Popen(command_jupytext, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, executable='/bin/bash')
            stdout, stderr = process_jupytext.communicate(input=payload['rmarkdown'].encode())
            process_jupytext.stdin.close()
            process_jupytext.wait()
            payload['notebook'] = stdout.decode()
            cell_index = payload['cell_index'] - bisect.bisect_right(payload['rmarkdown_offset_indices'], payload['cell_index']) - 1
        else:  # if 'notebook' in payload
            cell_index = payload['cell_index']
        kernel = payload['kernel']
        if isinstance(payload['notebook'], dict):
            payload['notebook'] = json.dumps(payload['notebook'])
        notebook = nbformat.reads(payload['notebook'], nbformat.NO_CONVERT)
        if 'rmarkdown' in payload:  # parsermd ignores md cells with \n only. We need to remove them here to keep consistency
            filtered_cells = [notebook.cells[0]]
            for i in range(1, len(notebook.cells)):
                cell = notebook.cells[i]
                if not (cell['cell_type'] == 'markdown' and all(line == os.linesep for line in cell['source']) and notebook.cells[i - 1]['cell_type'] == 'code'):
                    filtered_cells.append(cell)
            notebook.cells = filtered_cells
        common.logger.debug(cell_index)

        source = notebook.cells[cell_index].source

        if notebook.cells[cell_index].cell_type != 'code':
            # dummy extractor for non-code cells (e.g. markdown)
            extractor = DummyExtractor(notebook, source)
        else:
            # extractor based on the cell header
            try:
                extractor = HeaderExtractor(notebook, source)
            except jsonschema.ValidationError as e:
                return return_error('Error in cell header', e, stat=status.HTTP_400_BAD_REQUEST)

            # Extractor based on code analysis. Used if the cell has no header, or if some values are not specified in the header
            if not extractor.is_complete():
                if kernel == "IRkernel":
                    code_extractor = RExtractor(notebook, source)
                else:
                    code_extractor = PyExtractor(notebook, source)
                extractor.add_missing_values(code_extractor)

        extracted_nb = self.extract_cell_by_index(notebook, cell_index)
        if kernel == "IRkernel":
            extracted_nb = self.set_notebook_kernel(extracted_nb, 'R')
        else:
            extracted_nb = self.set_notebook_kernel(extracted_nb, 'python3')

        # initialize variables
        title = source.partition('\n')[0].strip()
        title = slugify(title) if title and title[0] == "#" else "Untitled"

        # if 'JUPYTERHUB_USER' in os.environ:
        #     title += '-' + slugify(os.environ['JUPYTERHUB_USER'])
        if 'JUPYTERHUB_USER' in payload:
            title += '-' + slugify(payload['JUPYTERHUB_USER'])

        # If any of these change, we create a new cell in the catalog. This matches the cell properties saved in workflows.
        # cell_identity_dict = {'title': title, 'params': extractor.params, 'inputs': extractor.ins, 'outputs': extractor.outs, }
        # cell_identity_str = json.dumps(cell_identity_dict, sort_keys=True)
        # node_id = hashlib.sha1(cell_identity_str.encode()).hexdigest()[:7]
        node_id = str(time.time_ns())[len('0x'):]

        cell = Cell(
            node_id=node_id,
            title=title,
            task_name=slugify(title.lower()),
            original_source=source,
            inputs=extractor.ins,
            outputs=extractor.outs,
            params={},
            confs=extractor.confs,
            dependencies=extractor.dependencies,
            container_source="",
            kernel=kernel,
            notebook_dict=extracted_nb.dict()
        )
        cell.integrate_configuration()
        extractor.params = extractor.extract_cell_params(cell.original_source)
        cell.add_params(extractor.params)
        cell.add_param_values(extractor.params)

        node = ConverterReactFlowChart.get_node(
            node_id,
            title,
            set(extractor.ins),
            set(extractor.outs),
            extractor.params,
        )

        chart = {'offset': {'x': 0, 'y': 0, }, 'scale': 1, 'nodes': {node_id: node}, 'links': {}, 'selected': {}, 'hovered': {}, }

        cell.chart_obj = chart
        return Response(cell.toJSON())


class CellsHandler(viewsets.ModelViewSet):
    common.logger.debug(f"CELL_GITHUB: {os.getenv('CELL_GITHUB')}")
    common.logger.debug(f"BASE_PATH: {os.getenv('BASE_PATH')}")
    queryset: QuerySet = Cell.objects.all()
    serializer_class = CellSerializer
    authentication_classes: list[BaseAuthentication] = [StaticTokenAuthentication]
    permission_classes: list[BasePermission] = [IsAuthenticated]
    cells_path: str = os.path.join(str(Path.home()), 'NaaVRE', 'cells')
    github_url_repos: str = 'https://api.github.com/repos'
    github_workflow_file_name: str = 'build-push-docker.yml'
    github_url: str = os.getenv('CELL_GITHUB')
    github_token: str = os.getenv('CELL_GITHUB_TOKEN')
    registry_url: str = os.getenv('REGISTRY_URL')
    repo_name: str = github_url.split('https://github.com/')[1]

    def write_cell_to_file(self, current_cell):
        Path('/tmp/workflow_cells/cells').mkdir(parents=True, exist_ok=True)
        with open('/tmp/workflow_cells/cells/' + current_cell.task_name + '.json', 'w') as f:
            f.write(current_cell.toJSON())
            f.close()

    def load_module_name_mapping(self):
        module_mapping_url = os.getenv('MODULE_MAPPING_URL')
        module_mapping = {}
        if module_mapping_url:
            resp = common.session.get(module_mapping_url)
            module_mapping = json.loads(resp.text)
        module_name_mapping_path = os.path.join(str(Path.home()), 'NaaVRE', 'module_name_mapping.json')
        if not os.path.exists(module_name_mapping_path):
            with open(module_name_mapping_path, 'w') as module_name_mapping_file:
                json.dump(module_mapping, module_name_mapping_file, indent=4)
            module_name_mapping_file.close()

        module_name_mapping_file = open(module_name_mapping_path)
        loaded_module_name_mapping = json.load(module_name_mapping_file)
        loaded_module_name_mapping.update(module_mapping)
        module_name_mapping_file.close()
        return loaded_module_name_mapping

    def get_files_info(self, cell=None):
        if not os.path.exists(self.cells_path):
            os.mkdir(self.cells_path)
        cell_path = os.path.join(self.cells_path, cell.task_name)

        cell_file_name = 'task.py'
        dockerfile_name = 'Dockerfile'
        environment_file_name = 'environment.yaml'

        notebook_file_name = None
        if 'visualize-' in cell.task_name:
            notebook_file_name = 'task.ipynb'
        if os.path.exists(cell_path):
            for files in os.listdir(cell_path):
                path = os.path.join(cell_path, files)
                if os.path.isfile(path):
                    os.remove(path)
        else:
            os.mkdir(cell_path)

        cell_file_path = os.path.join(cell_path, cell_file_name)
        dockerfile_file_path = os.path.join(cell_path, dockerfile_name)
        env_file_path = os.path.join(cell_path, environment_file_name)
        info = {
            'cell': {'file_name': cell_file_name, 'path': cell_file_path},
            'dockerfile': {'file_name': dockerfile_name, 'path': dockerfile_file_path},
            'environment': {'file_name': environment_file_name, 'path': env_file_path}
        }
        if notebook_file_name:
            info['notebook'] = {'file_name': notebook_file_name, 'path': os.path.join(cell_path, notebook_file_name)}
        return info

    def is_standard_module(self, module_name):
        if module_name in sys.builtin_module_names:
            return True
        installation_path = None
        try:
            installation_path = importlib.import_module(module_name).__file__
        except ImportError:
            return False
        linux_os = distro.id()
        return 'dist-packages' not in installation_path if linux_os == 'Ubuntu' else 'site-packages' not in installation_path

    def map_dependencies(self, dependencies=None, module_name_mapping=None):
        set_conda_deps = set([])
        set_pip_deps = set([])
        for dep in dependencies:
            if 'module' in dep and dep['module']:
                if '.' in dep['module']:
                    module_name = dep['module'].split('.')[0]
                else:
                    module_name = dep['module']
            elif 'name' in dep and dep['name']:
                module_name = dep['name']
            if module_name:
                conda_package = True
                pip_package = False
                if module_name in module_name_mapping['conda'].keys():
                    module_name = module_name_mapping['conda'][module_name]
                    pip_package = False
                    conda_package = True
                if module_name in module_name_mapping['pip'].keys():
                    module_name = module_name_mapping['pip'][module_name]
                    pip_package = True
                    conda_package = False
                if module_name is None:
                    continue
                if not self.is_standard_module(module_name):
                    if conda_package:
                        set_conda_deps.add(module_name)
                    if pip_package:
                        set_pip_deps.add(module_name)
        return set_conda_deps, set_pip_deps

    def build_templates(self, cell=None, files_info=None, module_name_mapping=None):
        common.logger.debug('files_info: ' + str(files_info))
        common.logger.debug('cell.dependencies: ' + str(cell.dependencies))
        set_conda_deps, set_pip_deps = self.map_dependencies(dependencies=cell.dependencies, module_name_mapping=module_name_mapping, )
        loader = jinja2.FileSystemLoader(searchpath=f'{common.project_root}/templates')
        template_env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

        if cell.title.startswith('visualize-'):
            template_cell = template_env.get_template('vis_cell_template.jinja2')
            if cell.notebook_dict:
                notebook_path = os.path.join(files_info['cell']['path']).replace('.py', '.ipynb')
                with open(notebook_path, 'w') as f:
                    f.write(json.dumps(cell.notebook_dict, indent=4))
                    f.close()
        else:
            template_cell = template_env.get_template('py_cell_template.jinja2')
        template_dockerfile = template_env.get_template('dockerfile_template_conda.jinja2')

        compiled_code = template_cell.render(cell=cell, deps=cell.generate_dependencies(), types=cell.types, confs=cell.generate_configuration_dict())

        compiled_code = autopep8.fix_code(compiled_code)
        cell.container_source = compiled_code

        template_cell.stream(cell=cell, deps=cell.generate_dependencies(), types=cell.types, confs=cell.generate_configuration_dict()).dump(files_info['cell']['path'])
        template_dockerfile.stream(task_name=cell.task_name, base_image=cell.base_image).dump(
            files_info['dockerfile']['path'])

        template_conda = template_env.get_template('conda_env_template.jinja2')
        template_conda.stream(base_image=cell.base_image, conda_deps=list(set_conda_deps), pip_deps=list(set_pip_deps)).dump(files_info['environment']['path'])

    def git_hash(self, contents):
        s = hashlib.sha1()
        s.update(('blob %u\0' % len(contents)).encode('utf-8'))
        s.update(contents)
        return s.hexdigest()

    def create_or_update_cell_in_repository(self, task_name, repository, files_info):
        files_updated = False
        code_content_hash = None
        for f_type, f_info in files_info.items():
            f_name = f_info['file_name']
            f_path = f_info['path']
            with open(f_path, 'rb') as f:
                local_content = f.read()
                local_hash = self.git_hash(local_content)
                try:
                    remote_hash = repository.get_contents(path=task_name + '/' + f_name).sha
                except UnknownObjectException:
                    remote_hash = None
                common.logger.debug(f'local_hash: {local_hash}; remote_hash: {remote_hash}')
                if remote_hash is None:
                    repository.create_file(path=task_name + '/' + f_name, message=task_name + ' creation', content=local_content, )
                elif remote_hash != local_hash:
                    repository.update_file(path=task_name + '/' + f_name, message=task_name + ' update', content=local_content, sha=remote_hash, )
                    files_updated = True
                if f_type == 'cell':
                    code_content_hash = local_hash
        return files_updated, code_content_hash

    def query_registry_for_image(self, image_repo, image_name):
        m = re.match(r'^docker.io/(\w+)', image_name)
        if m:
            # Docker Hub
            url = f'https://hub.docker.com/v2/repositories/{m.group(1)}/{image_name}'
            headers = {}
        else:
            # OCI registries
            domain = image_repo.split('/')[0]
            path = '/'.join(image_repo.split('/')[1:])
            url = f'https://{domain}/v2/{path}/{image_name}/tags/list'
            # OCI registries require authentication, even for public registries.
            # The token should be set in the $OCI_TOKEN environment variable.
            # For ghcr.io, connections still succeed when $OCI_TOKEN is unset (this results in header "Authorization: Bearer None", which grants access to public registries, although it is not officially documented). If this fails, or when accessing private registries, OCI_TOKEN should be a base64-encoded GitHub classic access token with the read:packages scope.
            headers = {"Authorization": f"Bearer {os.getenv('OCI_TOKEN')}", }
        response = common.session.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

    def dispatch_github_workflow(self, owner, repository_name, task_name, files_info, repository_token, image, wf_id=None, image_version=None):
        url = CellsHandler.github_url_repos + '/' + owner + '/' + repository_name + '/actions/workflows/' + CellsHandler.github_workflow_file_name + '/dispatches'
        resp = common.session.post(
            url=url,
            json={
                'ref': 'refs/heads/main',
                'inputs': {
                    'build_dir': task_name,
                    'dockerfile': files_info['dockerfile']['file_name'],
                    'image_repo': image,
                    'image_tag': task_name,
                    'id': wf_id,
                    'image_version': image_version,
                }
            },
            verify=False,
            headers={'Accept': 'application/vnd.github.v3+json', 'Authorization': 'token ' + repository_token}
        )
        return resp

    @classmethod
    def get_registry_url(cls, registry_url, github_url):
        """ Convert registry URL

        https://hub.docker.com/u/my_username/ -> docker.io/my_username
        oci://ghcr.io/my_username/my_repo/ -> ghcr.io/my_username/my_repo
        oci://my_domain/my/custom/path/ -> my_domain/my/custom/path
        None -> ghcr.io url, derived from github_url

        Resulting urls can be converted to pullable, e.g.:

        docker pull {url}/{image_name}:{tag}

        where image_name doesn't contain any path information (e.g. my-cell-name)

        """
        if registry_url:
            m = re.match(r'^https://hub\.docker\.com/u/(\w+)/?$', registry_url)
            if m:
                return f"docker.io/{m.group(1)}"
            m = re.match(r'^oci://([\w\./-]+?)/?$', registry_url)
            if m:
                return m.group(1)
            raise ValueError(f"Could not parse registry url: {registry_url}")
        else:
            m = re.match(r'^https://github.com/([\w-]+/[\w-]+)(?:\.git)?', github_url)
            if m:
                return f"ghcr.io/{m.group(1).lower()}"

    def get_registry_credentials(self) -> list[dict[str, str]]:
        return [Repository(CellsHandler.registry_url, CellsHandler.registry_url, None).__dict__]

    @classmethod
    def get_repositories(cls) -> list[dict[str, str]]:
        return [Repository(CellsHandler.repo_name, CellsHandler.github_url, CellsHandler.github_token).__dict__]

    def create(self, request: Request, *args, **kwargs):
        try:
            Cell_field_names = [f.name for f in Cell._meta.get_fields()]
            filtered_incoming_body = {k: request.data[k] for k in Cell_field_names if k in request.data}
            current_cell = Cell(**filtered_incoming_body)
            # current_cell = Cell(**request.data)
            current_cell.clean_code()
            current_cell.clean_title()
            current_cell.clean_task_name()
        except Exception as ex:
            return return_error('Error setting cell', ex)

        common.logger.debug('current_cell: ' + current_cell.toJSON())
        all_vars = current_cell.params + current_cell.inputs + current_cell.outputs
        for param_name in all_vars:
            if param_name not in current_cell.types:
                return return_error(f'{param_name} not in types')

        if not hasattr(current_cell, 'base_image'):
            return return_error(f'{current_cell.task_name} has not selected base image')
        try:
            serializer: CellSerializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance, created = Cell.objects.update_or_create(node_id=serializer.validated_data['node_id'], defaults=serializer.validated_data)
        except Exception as ex:
            return return_error('Error adding or updating cell in catalog', ex)

        if os.getenv('DEBUG'):
            self.write_cell_to_file(current_cell)

        if not os.path.exists(self.cells_path):
            os.makedirs(self.cells_path, exist_ok=True)

        cell_path = os.path.join(self.cells_path, current_cell.task_name)

        if os.path.exists(cell_path):
            for files in os.listdir(cell_path):
                path = os.path.join(cell_path, files)
                if os.path.isfile(path):
                    os.remove(path)
        else:
            os.makedirs(cell_path, exist_ok=True)

        registry_credentials = self.get_registry_credentials()
        if not registry_credentials or len(registry_credentials) <= 0:
            return return_error('Registry credentials not found')
        image_repo = registry_credentials[0]['url']
        if not image_repo:
            return return_error(f'Registry not found. Registry credentials:{os.linesep}{registry_credentials}')

        if current_cell.kernel == "IRkernel":
            files_info = RContainerizer.get_files_info(cell=current_cell, cells_path=CellsHandler.cells_path)
            RContainerizer.build_templates(cell=current_cell, files_info=files_info, module_name_mapping=self.load_module_name_mapping(), )
        elif 'python' in current_cell.kernel.lower():
            files_info = self.get_files_info(cell=current_cell)
            self.build_templates(cell=current_cell, files_info=files_info, module_name_mapping=self.load_module_name_mapping(), )
        else:
            return return_error(f'Kernel {current_cell.kernel} not supported')

        # upload to GIT
        cat_repositories = self.get_repositories()

        repo_token = cat_repositories[0]['token']
        if not repo_token:
            return return_error('Repository token not found')

        gh_token = Github(cat_repositories[0]['token'])
        url_repos = cat_repositories[0]['url']
        if not url_repos:
            return return_error('Repository url not found')

        owner = url_repos.split('https://github.com/')[1].split('/')[0]
        repository_name = url_repos.split('https://github.com/')[1].split('/')[1]
        if '.git' in repository_name:
            repository_name = repository_name.split('.git')[0]
        retry_count: int = 0
        while True:
            try:
                gh_repository = gh_token.get_repo(owner + '/' + repository_name)
                break
            except Exception as ex:
                time.sleep(common.retry_delay(retry_count))
                retry_count += 1
                if retry_count >= common.max_retry_count:
                    return return_error(f'Error getting repository', ex)
        do_dispatch_github_workflow, image_version = self.create_or_update_cell_in_repository(task_name=current_cell.task_name, repository=gh_repository, files_info=files_info, )
        wf_id = str(uuid.uuid4())

        if os.getenv('DEBUG') and os.getenv('DEBUG').lower() == 'true':
            do_dispatch_github_workflow = True
        else:
            image_info = self.query_registry_for_image(image_repo=image_repo, image_name=current_cell.task_name, )
            common.logger.debug(f'image_info: {image_info}')
            if not image_info:
                do_dispatch_github_workflow = True

        image_version = image_version[:7]
        if do_dispatch_github_workflow:
            resp = self.dispatch_github_workflow(owner, repository_name, current_cell.task_name, files_info, repo_token, image_repo, wf_id=wf_id, image_version=image_version)
            if resp.status_code != 201 and resp.status_code != 200 and resp.status_code != 204:
                return return_error(resp.text)
            current_cell.set_image_version(image_version)
            Cell.objects.filter(task_name=current_cell.task_name).delete()
            current_cell.save()

        return Response({'wf_id': wf_id, 'dispatched_github_workflow': do_dispatch_github_workflow, 'image_version': image_version})


CellsHandler.registry_url = CellsHandler.get_registry_url(CellsHandler.registry_url, CellsHandler.github_url)
