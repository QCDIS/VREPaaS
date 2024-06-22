import requests
import json
import os
import time
import argparse
import re

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('in_def', nargs='+')
arg_parser.add_argument('--in-no', action='append', nargs='+')
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

if args.in_no is not None:
    for test_info in args.in_no:
        endpoint: str = test_info[0]
        files: list[str] = [f'{endpoint}.{no}.json' for no in test_info[1:]]
        test(endpoint, files)
