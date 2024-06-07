import os
import json
import traceback
import copy
import hashlib
from typing import Optional

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


def return_error(err_msg: str, e: Optional[Exception], stat: status = status.HTTP_400_BAD_REQUEST) -> Response:
    common.logger.error(err_msg, e)
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


class BaseImageHandler(APIView, Catalog):
    authentication_classes = [StaticTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        payload = request.data
        common.logger.debug('BaseImageHandler. payload: ' + str(payload))
        base_image = payload['image']
        cell = Catalog.editor_buffer
        cell.base_image = base_image


class CellsHandler(APIView, Catalog):
    authentication_classes = [StaticTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        return return_error('Operation not supported.', stat=status.HTTP_400_BAD_REQUEST)

    def post(self, request: Request):
        try:
            current_cell = Catalog.editor_buffer
            current_cell.clean_code()
            current_cell.clean_title()
            current_cell.clean_task_name()
        except Exception as ex:
            return return_error('Error setting cell', ex, status.HTTP_400_BAD_REQUEST)

        common.logger.debug('current_cell: ' + current_cell.toJSON())
        all_vars = current_cell.params + current_cell.inputs + current_cell.outputs
        for param_name in all_vars:
            if param_name not in current_cell.types:
                return return_error(f'{param_name} not in types', stat=status.HTTP_400_BAD_REQUEST)

        if not hasattr(current_cell, 'base_image'):
            return return_error(f'{current_cell.task_name} has not selected base image', stat=status.HTTP_400_BAD_REQUEST)
        try:
            doc_cell = Catalog.get_cell_from_og_node_id(current_cell.node_id)
            if doc_cell:
                Catalog.update_cell(current_cell)
            else:
                Catalog.add_cell(current_cell)
        except Exception as ex:
            return return_error('Error adding or updating cell in catalog', ex, status.HTTP_400_BAD_REQUEST)

