version_settings(constraint='>=0.22.2')


# API

docker_build(
    'qcdis/vreapi',
    context='.',
    dockerfile='deploy/vreapis.dev.dockerfile',
    only=['./vreapis/'],
    live_update=[
        sync('./vreapis', '/app'),
        run('cd /app && /opt/venv/bin/pip install -r requirements.txt', trigger='./vreapis/requirements.txt')
    ]
)

k8s_yaml('deploy/vreapis.yaml')

k8s_resource(
    'vreapi-deployment',
    port_forwards='8000:8000',
    labels=['vreapi']
)

# Panel

docker_build(
    'qcdis/vreapp',
    context='.',
    dockerfile='deploy/vre-panel.dev.dockerfile',
    only=['./vre-panel/'],
    live_update=[
        sync('./vre-panel', '/app')
    ]
)

k8s_yaml('deploy/vre-panel.yaml')

k8s_resource(
    'vreapp-deployment',
    port_forwards='3000:3000',
    labels=['vreapp']
)
