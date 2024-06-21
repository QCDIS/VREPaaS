import requests
import json
import os
import sys
import time

script_path: str = os.path.dirname(os.path.realpath(__file__))
endpoint: str = f"{os.getenv('API_ENDPOINT')}/api/containerizer"
headers: dict = {
    "Content-Type": "application/json",
    "Authorization": f"Token {os.getenv('NAAVRE_API_TOKEN')}",
}
session = requests.Session()

for i in range(1, len(sys.argv)):
    with open(f'{script_path}/dat/{sys.argv[i]}.json') as f:
        body: dict[str, any] = json.load(f)
        match sys.argv[i]:
            case 'addcell':
                body['node_id'] = str(hex(time.time_ns())[len('0x'):])
    response = session.post(f'{endpoint}/{sys.argv[i]}', json.dumps(body), headers=headers, verify=False)
    print(response.text)
