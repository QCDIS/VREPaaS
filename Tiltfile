version_settings(constraint='>=0.22.2')
secret_settings (disable_scrub=True)

# API

docker_build(
    'qcdis/vreapi',
    context='.',
    dockerfile='tilt/vreapis.dev.dockerfile',
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
    labels=['vreapi']
)

# Panel

docker_build(
    'qcdis/vreapp',
    context='.',
    dockerfile='tilt/vre-panel.dev.dockerfile',
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
    labels=['vreapp']
)
