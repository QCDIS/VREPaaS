version_settings(constraint='>=0.22.2')
secret_settings (disable_scrub=True)
load('ext://helm_remote', 'helm_remote')

helm_remote(
    'vrepaas',
    repo_name='oci://ghcr.io/qcdis/charts',
    version='0.5.1',
    values=[
        './tilt/helm-values-dev.yaml',
        './tilt/helm-values-secrets.yaml',
    ],
)

docker_build(
    'qcdis/vreapi',
    context='.',
    dockerfile='tilt/vreapis/Dockerfile',
    only=['./vreapis/'],
    live_update=[
        sync('./vreapis', '/app'),
        run('cd /app && /opt/venv/bin/python manage.py makemigrations'),
        run('cd /app && /opt/venv/bin/python manage.py migrate'),
        run('cd /app && /opt/venv/bin/pip install -r requirements.txt', trigger='./vreapis/requirements.txt'),
    ],
)

docker_build(
    'qcdis/vreapp',
    context='.',
    dockerfile='tilt/vre-panel/Dockerfile',
    only=['./vre-panel/'],
    live_update=[
        sync('./vre-panel', '/app'),
        run('cd /app && npm install', trigger=['./vre-panel/package.json'])
    ],
)

k8s_resource(
    'vrepaas-vreapi',
    links=[
        'https://paas.minikube.test/vre-api-test/api/',
        'https://paas.minikube.test/vre-api-test/admin/',
    ],
)

k8s_resource(
    'vrepaas-vreapp',
    links=[
        'https://paas.minikube.test/vreapp/',
    ],
)
