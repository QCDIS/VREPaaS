version_settings(constraint='>=0.22.2')
secret_settings (disable_scrub=True)
load('ext://helm_remote', 'helm_remote')

# API

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
    ]
)

k8s_yaml(['tilt/vreapis.yaml','tilt/django-secrets.yaml','tilt/vre-api-config.yaml'])

k8s_resource(
    'vreapi-deployment',
    port_forwards='8000:8000',
    labels=['vreapi'],
    links=[
        'http://localhost:8000/paas/api/api/',
        'http://localhost:8000/paas/api/admin/',
    ],
    resource_deps=['db-deployment']
)

# Panel

docker_build(
    'qcdis/vreapp',
    context='.',
    dockerfile='tilt/vre-panel/Dockerfile',
    only=['./vre-panel/'],
    live_update=[
        sync('./vre-panel', '/app'),
        run('cd /app && npm install', trigger=['./vre-panel/package.json'])
    ]
)

k8s_yaml(['tilt/vre-panel.yaml','tilt/vre-panel-secrets.yaml'])

k8s_resource(
    'vreapp-deployment',
    port_forwards='3000:3000',
    labels=['vreapp'],
    links=[
        'http://localhost:3000/paas/app/',
    ],
    resource_deps=['vreapi-deployment']
)

# DB

k8s_yaml([ 'tilt/vre-depts-db.yaml'])

k8s_resource(
    'db-deployment',
    labels=['db'],
)


# Ingress

k8s_yaml([ 'tilt/ingress.yaml'])

helm_remote('ingress-nginx',
            version="4.0.2",
            repo_name='ingress-nginx',
            set=['controller.admissionWebhooks.enabled=false'],
            values=['tilt/ingress-nginx-values.yaml'],
            repo_url='https://kubernetes.github.io/ingress-nginx')
