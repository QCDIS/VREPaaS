import requests
import json
import os
import sys

script_path: str = os.path.dirname(os.path.realpath(__file__))
endpoint: str = f"{os.getenv('API_ENDPOINT')}/api/containerizer/extract"
headers: dict = {
    "Content-Type": "application/json",
    "Authorization": f"Token {os.getenv('NAAVRE_API_TOKEN')}",
}
session = requests.Session()

for i in range(1, len(sys.argv)):
    with open(f'{script_path}/dat/{sys.argv[i]}.json') as f:
        body: dict[str, any] = json.load(f)
    response = session.post(endpoint, json.dumps(body), headers=headers, verify=False)
    print(response.text)