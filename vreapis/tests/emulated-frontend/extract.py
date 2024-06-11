import requests
import json
import os

script_path: str = os.path.dirname(os.path.realpath(__file__))
endpoint: str = f"{os.getenv('API_ENDPOINT')}/api/containerizer/extract/"
headers: dict = {"Authorization": f"Token {os.getenv('NAAVRE_API_TOKEN')}"}
session = requests.Session()

with open(f'{script_path}/dat/extract.json') as f:
    bodies: list[dict[str, any]] = json.load(f)

for body in bodies:
    response = session.post(endpoint, body, headers=headers, verify=False)
    print(response.text)
