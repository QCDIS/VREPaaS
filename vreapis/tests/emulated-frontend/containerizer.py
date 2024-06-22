import requests
import json
import os
import time
import argparse
import re

arg_parser = argparse.ArgumentParser(description='''
These tests emulate a frontend to test the endpoints of VRE PaaS API.
At this moment, folder `dat` contains all the test input data. Each file represents an entire request body.
Some files contain only 1 segment of extension `.json`. This indicates that the file is the only test case.
Some files contain 2 segments of extension (ex. `.1.json`). The substring between 2 dots is the ID of the test case (`1` in this example).
'''.strip())
arg_parser.add_argument('in_def', nargs='+', help='''
Default: Test the designated endpoint using all the existing request bodies.
'''.strip())
arg_parser.add_argument('--in-id', action='append', nargs='+', help='''
Specify test cases by ID: Test the designated endpoint using the request bodies with the specified IDs. 
'''.strip())
args = arg_parser.parse_args()

script_path: str = os.path.dirname(os.path.realpath(__file__))
API_ENDPOINT: str = f"{os.getenv('API_ENDPOINT')}/api/containerizer"
headers: dict = {
    "Content-Type": "application/json",
    "Authorization": f"Token {os.getenv('NAAVRE_API_TOKEN')}",
}
session = requests.Session()


def test(endpoint: str, files: list[str]):
    for file in files:
        with open(f'{script_path}/dat/{file}') as f:
            body: dict[str, any] = json.load(f)
            match endpoint:
                case 'addcell':
                    body['node_id'] = str(hex(time.time_ns())[len('0x'):])
        response = session.post(f'{API_ENDPOINT}/{endpoint}', json.dumps(body), headers=headers, verify=False)
        print(response.text)


for endpoint in args.in_def:
    file_pattern = re.compile(fr'{endpoint}(\..+)?.json')
    files: list[str] = os.listdir(f'{script_path}/dat')
    request_body_files: list[str] = [file for file in files if file_pattern.match(file)]
    test(endpoint, request_body_files)

if args.in_id is not None:
    for test_info in args.in_id:
        endpoint: str = test_info[0]
        files: list[str] = [f'{endpoint}.{id}.json' for id in test_info[1:]]
        test(endpoint, files)
