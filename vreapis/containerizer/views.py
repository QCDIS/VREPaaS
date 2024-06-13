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

import autopep8
from distro import distro
import jinja2
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
import requests
import nbformat
import jsonschema
from slugify import slugify
from github import Github, UnknownObjectException

from containerizer.RContainerizer import RContainerizer
from services.extractor.extractor import DummyExtractor
from services.extractor.headerextractor import HeaderExtractor
from services.extractor.pyextractor import PyExtractor
from services.extractor.rextractor import RExtractor
from services.converter import ConverterReactFlowChart
import utils.cors
from auth.simple import StaticTokenAuthentication
from db.catalog import Catalog
from db.cell import Cell

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


class ExtractorHandler(APIView, Catalog):
    authentication_classes = [StaticTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def extract_cell_by_index(self, notebook, cell_index):
        new_nb = copy.deepcopy(notebook)
        if cell_index < len(notebook.cells):
            new_nb.cells = [notebook.cells[cell_index]]
            return new_nb

    def set_notebook_kernel(self, notebook, kernel):
        new_nb = copy.deepcopy(notebook)
        # Replace kernel name in the notebook metadata
        new_nb.metadata.kernelspec.name = kernel
        new_nb.metadata.kernelspec.display_name = kernel
        new_nb.metadata.kernelspec.language = kernel
        return new_nb

    def get(self, request: Request):
        return return_error("Operation not supported.", stat=status.HTTP_400_BAD_REQUEST)

    def post(self, request: Request):
        payload = request.data
        common.logger.debug('ExtractorHandler. payload: ' + json.dumps(payload, indent=4))
        kernel = payload['kernel']
        cell_index = payload['cell_index']
        notebook = nbformat.reads(json.dumps(payload['notebook']), nbformat.NO_CONVERT)

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

        if 'JUPYTERHUB_USER' in os.environ:
            title += '-' + slugify(os.environ['JUPYTERHUB_USER'])

        # If any of these change, we create a new cell in the catalog. This matches the cell properties saved in workflows.
        cell_identity_dict = {'title': title, 'params': extractor.params, 'inputs': extractor.ins, 'outputs': extractor.outs, }
        cell_identity_str = json.dumps(cell_identity_dict, sort_keys=True)
        node_id = hashlib.sha1(cell_identity_str.encode()).hexdigest()[:7]

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
        Catalog.editor_buffer = copy.deepcopy(cell)
        return Response(cell.toJSON())


class TypesHandler(APIView, Catalog):
    authentication_classes = [StaticTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        payload = request.data
        common.logger.debug('TypesHandler. payload: ' + str(payload))
        port = payload['port']
        p_type = payload['type']
        cell = Catalog.editor_buffer
        cell.types[port] = p_type
        return Response({})  # must return a Response, or 500 occurs


class BaseImageHandler(APIView, Catalog):
    authentication_classes = [StaticTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        payload = request.data
        common.logger.debug('BaseImageHandler. payload: ' + str(payload))
        base_image = payload['image']
        cell = Catalog.editor_buffer
        cell.base_image = base_image
        return Response({})


class CellsHandler(APIView, Catalog):
    authentication_classes = [StaticTokenAuthentication]
    permission_classes = [IsAuthenticated]
    cells_path = os.path.join(str(Path.home()), 'NaaVRE', 'cells')
    github_url_repos = 'https://api.github.com/repos'
    github_workflow_file_name = 'build-push-docker.yml'

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

    def get(self, request: Request):
        return return_error('Operation not supported.')

    def post(self, request: Request):
        try:
            current_cell = Catalog.editor_buffer
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
            doc_cell = Catalog.get_cell_from_og_node_id(current_cell.node_id)
            if doc_cell:
                Catalog.update_cell(current_cell)
            else:
                Catalog.add_cell(current_cell)
        except Exception as ex:
            return return_error('Error adding or updating cell in catalog', ex)

        if os.getenv('DEBUG'):
            self.write_cell_to_file(current_cell)

        if not os.path.exists(self.cells_path):
            os.mkdir(self.cells_path)

        cell_path = os.path.join(self.cells_path, current_cell.task_name)

        if os.path.exists(cell_path):
            for files in os.listdir(cell_path):
                path = os.path.join(cell_path, files)
                if os.path.isfile(path):
                    os.remove(path)
        else:
            os.mkdir(cell_path)

        registry_credentials = Catalog.get_registry_credentials()
        if not registry_credentials or len(registry_credentials) <= 0:
            return return_error('Registry credentials not found')
        image_repo = registry_credentials[0]['url']
        if not image_repo:
            return return_error('Registry not found')

        if current_cell.kernel == "IRkernel":
            files_info = RContainerizer.get_files_info(cell=current_cell, cells_path=CellsHandler.cells_path)
            RContainerizer.build_templates(cell=current_cell, files_info=files_info, module_name_mapping=self.load_module_name_mapping(), )
        elif 'python' in current_cell.kernel.lower():
            files_info = self.get_files_info(cell=current_cell)
            self.build_templates(cell=current_cell, files_info=files_info, module_name_mapping=self.load_module_name_mapping(), )
        else:
            return return_error(f'Kernel {current_cell.kernel} not supported')

        # upload to GIT
        cat_repositories = Catalog.get_repositories()

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
            if not image_info:
                do_dispatch_github_workflow = True

        image_version = image_version[:7]
        if do_dispatch_github_workflow:
            resp = self.dispatch_github_workflow(owner, repository_name, current_cell.task_name, files_info, repo_token, image_repo, wf_id=wf_id, image_version=image_version)
            if resp.status_code != 201 and resp.status_code != 200 and resp.status_code != 204:
                return return_error(resp.text)
            current_cell.set_image_version(image_version)
            Catalog.delete_cell_from_task_name(current_cell.task_name)
            Catalog.add_cell(current_cell)

        return Response({'wf_id': wf_id, 'dispatched_github_workflow': do_dispatch_github_workflow, 'image_version': image_version})
