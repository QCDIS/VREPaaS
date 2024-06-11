import logging
import os

import jinja2

import common

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# Create a formatter for the log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the formatter to the handler
handler.setFormatter(formatter)

# Add the handler to the logger
common.logger.addHandler(handler)


class RContainerizer:
    @staticmethod
    def get_files_info(cell=None, cells_path=None):
        if not os.path.exists(cells_path):
            os.mkdir(cells_path)
        cell_path = os.path.join(cells_path, cell.task_name)

        cell_file_name = 'task.R'
        dockerfile_name = 'Dockerfile'
        environment_file_name = 'environment.yaml'

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
        return {
            'cell': {'file_name': cell_file_name, 'path': cell_file_path},
            'dockerfile': {'file_name': dockerfile_name, 'path': dockerfile_file_path},
            'environment': {'file_name': environment_file_name, 'path': env_file_path},
        }

    @staticmethod
    def map_dependencies(dependencies, module_name_mapping):
        dependencies = map(lambda x: 'r-' + x['name'], dependencies)
        dependencies = map(lambda x: module_name_mapping.get('r', {}).get(x, x), dependencies)
        set_conda_deps = set(dependencies)
        set_pip_deps = set()
        set_conda_deps.discard(None)
        set_conda_deps.discard(None)
        return set_conda_deps, set_pip_deps

    @staticmethod
    def build_templates(cell=None, files_info=None, module_name_mapping=None):
        # we also want to always add the id to the input parameters
        inputs = cell.inputs
        types = cell.types
        inputs.append('id')
        cell.concatenate_all_inputs()
        types['id'] = 'str'
        common.logger.debug("inputs: " + str(cell.inputs))
        common.logger.debug("types: " + str(cell.types))
        common.logger.debug("params: " + str(cell.params))
        common.logger.debug("outputs: " + str(cell.outputs))

        common.logger.debug('files_info: ' + str(files_info))
        common.logger.debug('cell.dependencies: ' + str(cell.dependencies))

        loader = jinja2.FileSystemLoader(searchpath=f'{common.project_root}/templates')
        template_env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

        template_cell = template_env.get_template('R_cell_template.jinja2')
        template_dockerfile = template_env.get_template('dockerfile_template_conda.jinja2')

        compiled_code = template_cell.render(cell=cell, deps=cell.generate_dependencies(), types=cell.types, confs=cell.generate_configuration())
        cell.container_source = compiled_code
        dependencies = cell.generate_dependencies()
        r_dependencies = []
        for dep in dependencies:
            r_dep = dep.replace('import ', '')
            install_packages = 'if (!requireNamespace("' + r_dep + '", quietly = TRUE)) {\n\tinstall.packages("' + r_dep + '", repos="http://cran.us.r-project.org")\n}'
            r_dependencies.append(install_packages)
            library = 'library(' + r_dep + ')'
            r_dependencies.append(library)

        template_cell.stream(cell=cell, deps=r_dependencies, types=cell.types, confs=cell.generate_configuration()).dump(files_info['cell']['path'])
        template_dockerfile.stream(task_name=cell.task_name, base_image=cell.base_image).dump(files_info['dockerfile']['path'])

        set_conda_deps, set_pip_deps = RContainerizer.map_dependencies(cell.dependencies, module_name_mapping)
        common.logger.debug('cell.dependencies.conda: ' + str(cell.dependencies))
        template_conda = template_env.get_template('conda_env_template.jinja2')
        template_conda.stream(base_image=cell.base_image, conda_deps=list(set_conda_deps), pip_deps=list(set_pip_deps)).dump(files_info['environment']['path'])
