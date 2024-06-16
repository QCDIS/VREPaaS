import logging
import os
import re
from pathlib import Path

from tinydb import TinyDB, where

from .cell import Cell
from .repository import Repository
from .sdia_credentials import SDIACredentials

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Catalog:
    naa_vre_path = os.path.join(str(Path.home()), 'NaaVRE')

    if not os.path.exists(naa_vre_path):
        os.mkdir(naa_vre_path)

    db_path = os.path.join(naa_vre_path, 'NaaVRE_db.json')
    db = TinyDB(db_path)

    cells = db.table('cells')
    workflows = db.table('workflows')
    repositories = db.table('repositories')
    gh_credentials = db.table('gh_credentials')
    registry_credentials = db.table('registry_credentials')
    search_entry = db.table('search_entries')

    @classmethod
    def add_search_entry(cls, query: dict):
        cls.search_entry.insert(query)

    @classmethod
    def update_cell(cls, cell: Cell):
        cls.cells.update(cell.__dict__, where('node_id') == cell.node_id)

    @classmethod
    def get_search_entries(cls):
        return cls.search_entry.all()

    @classmethod
    def delete_all_search_entries(cls):
        return cls.search_entry.truncate()

    @classmethod
    def add_cell(cls, cell: Cell):
        cls.cells.insert(cell.__dict__)

    @classmethod
    def delete_cell_from_task_name(cls, task_name: str):
        cell = cls.cells.search(where('task_name') == task_name)
        cls.cells.remove(where('task_name') == task_name)

    @classmethod
    def delete_cell_from_title(cls, title: str):
        cell = cls.cells.search(where('title') == title)
        cls.cells.remove(where('title') == title)

    @classmethod
    def get_all_cells(cls):
        return cls.cells.all()

    @classmethod
    def get_registry_credentials(cls):
        credentials = cls.registry_credentials.all()
        return credentials

    @classmethod
    def get_repository_credentials(cls):
        credentials = cls.repositories.all()
        return credentials

    @classmethod
    def get_registry_credentials_from_name(cls, name: str):
        res = cls.registry_credentials.search(where('name') == name)
        if res:
            return res[0]

    @classmethod
    def add_registry_credentials(cls, cred: Repository):
        cls.registry_credentials.insert(cred.__dict__)

    @classmethod
    def add_repository_credentials(cls, cred: Repository):
        cls.repositories.insert(cred.__dict__)

    @classmethod
    def get_gh_credentials(cls):
        credentials = cls.gh_credentials.all()
        if len(credentials) > 0:
            return credentials[0]

    @classmethod
    def delete_all_gh_credentials(cls):
        cls.gh_credentials.truncate()

    @classmethod
    def delete_all_cells(cls):
        cls.cells.truncate()

    @classmethod
    def delete_all_repository_credentials(cls):
        cls.repositories.truncate()
        credentials = cls.repositories.all()
        ids = []
        for credential in credentials:
            ids.append(credential.doc_id)
        cls.repositories.remove(doc_ids=ids)
        cls.repositories.truncate()

    @classmethod
    def delete_all_registry_credentials(cls):
        # Looks bad but for now I could not find a way to remove all
        credentials = cls.registry_credentials.all()
        ids = []
        for credential in credentials:
            ids.append(credential.doc_id)
        cls.registry_credentials.remove(doc_ids=ids)
        cls.registry_credentials.truncate()

    @classmethod
    def add_gh_credentials(cls, cred: Repository):
        cls.repositories.insert(cred.__dict__)
        cls.gh_credentials.insert(cred.__dict__)

    @classmethod
    def delete_gh_credentials(cls, url: str):
        cls.gh_credentials.remove(where('url') == url)

    @classmethod
    def get_credentials_from_username(cls, cred_username) -> SDIACredentials:
        res = cls.sdia_credentials.search(where('username') == cred_username)
        if res:
            return res[0]

    @classmethod
    def get_sdia_credentials(cls):
        return cls.sdia_credentials.all()

    @classmethod
    def get_cell_from_og_node_id(cls, og_node_id) -> Cell:
        res = cls.cells.search(where('node_id') == og_node_id)
        if res:
            return res[0]
        else:
            logger.warning('Cell not found for og_node_id: ' + og_node_id)

    @classmethod
    def get_repositories(cls) -> list:
        res = cls.repositories.all()
        return res

    @classmethod
    def get_repository_from_name(cls, name: str) -> Repository:
        res = cls.repositories.search(where('name') == name)
        if res:
            return res[0]

    @classmethod
    def cast_document_to_cell(cls, cell_document):
        if not cell_document:
            return None

        return Cell(
            title=cell_document.get('title', ''),
            task_name=cell_document.get('task_name', ''),
            original_source=cell_document.get('original_source', ''),
            inputs=cell_document.get('inputs', []),
            outputs=cell_document.get('outputs', []),
            params=cell_document.get('params', []),
            confs=cell_document.get('confs', {}),
            dependencies=cell_document.get('dependencies', []),
            container_source=cell_document.get('container_source', ''),
            chart_obj=cell_document.get('chart_obj', {}),
            node_id=cell_document.get('node_id', ''),
            kernel=cell_document.get('kernel', ''),
            notebook_dict=cell_document.get('notebook_dict', {})
        )

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


github_url: str = os.getenv('CELL_GITHUB')
github_token: str = os.getenv('CELL_GITHUB_TOKEN')
registry_url: str = os.getenv('REGISTRY_URL')
# force: bool = True if os.getenv('FORCED_CREDENTIALS_REPLACEMENT', 'false').lower() == 'true' else 'false'
registry_url = Catalog.get_registry_url(registry_url, github_url)

input_repository_credentials = Repository(github_url.split('https://github.com/')[1], github_url, github_token)
Catalog.add_gh_credentials(input_repository_credentials)
Catalog.add_repository_credentials(input_repository_credentials)

input_registry_credentials = Repository(registry_url, registry_url, None)
Catalog.add_registry_credentials(input_registry_credentials)
