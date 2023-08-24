# VREPaaS


## Development 
This project is usgin Django rest framework. 

### Install Anaconda

Install Anaconda from these instructions: https://linuxize.com/post/how-to-install-anaconda-on-ubuntu-20-04/

Close the terminal and start a new one to activate conda.

### Create and activate conda environment

Create and activate conda environment:
```shell
conda env update --file environment.yaml
```

#### Install tilt
Install [tilt](https://docs.tilt.dev/install.html) via conda 

```shell
conda install -c conda-forge tilt 
```

#### Install minikube

```shell
conda install -c conda-forge minikube 
```

Follow step 3 of the [minikube ingress-dns setup guide](https://minikube.sigs.k8s.io/docs/handbook/addons/ingress-dns/).

#### Add secrets

Create `tilt/helm-values-secrets.yaml` and fill-in the following:

```yaml
global:
  keycloak:
    url:
    realm:
    client_id:
    client_secret_key:

  argo:
    namespace:
    url:
    token:
```

#### Start Cluster

```shell
minikube start
minikube addons enable ingress
minikube addons enable ingress-dns
minikube dashboard  # optional
```

#### Run tilt

```shell
tilt up
```

# Encrypt secrets 


conda install -c conda-forge git-crypt


# Deploy Webapp
```
$make deploy-app
```


# Deploy API
```
$make deploy-api
```

# API Admin
To add/reomve resources go to: https://HOST/vre-api-test/admin/

## Admin Credentials
The admin credentials are generated by k8s/vreapis/secreats.yaml file with the value 'superuser-passwor'
The username is hardcoded in k8s/vreapis/deplyment.yaml in the env 'DJANGO_SUPERUSER_USERNAME'



# Argo Workflows

## Generate Token

```shell
kubectl apply -f - <<EOF
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: vre-api
  namespace: argo
rules:
  - verbs:
      - get
      - watch
      - patch
      - delete
    apiGroups:
      - ''
    resources:
      - pods
  - verbs:
      - get
      - watch
      - patch
    apiGroups:
      - ''
    resources:
      - pods/log
  - verbs:
      - create
    apiGroups:
      - ''
    resources:
      - pods/exec
  - verbs:
      - list
      - watch
      - create
      - get
      - update
      - delete
    apiGroups:
      - argoproj.io
    resources:
      - workflowtasksets
      - workflowartifactgctasks
      - workflowtemplates
      - workflows
      - cronworkflows
  - verbs:
      - patch
    apiGroups:
      - argoproj.io
    resources:
      - workflowtasksets/status
      - workflowartifactgctasks/status
      - workflows/status
EOF
```

```shell
kubectl create sa vre-api -n argo
```

```shell
kubectl create rolebinding vre-api --role=vre-api --serviceaccount=argo:vre-api -n argo
```

```shell
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  namespace: argo
  name: vre-api.service-account-token
  annotations:
    kubernetes.io/service-account.name: vre-api
type: kubernetes.io/service-account-token
EOF
```

```shell
ARGO_TOKEN="Bearer $(kubectl get secret vre-api.service-account-token -n argo -o=jsonpath='{.data.token}' | base64 --decode)"
```

```shell
echo -n $ARGO_TOKEN | base64 -w 0
```



# Authorization 

## Token 

1. Create a user in the Django admin panel
2. Create a token for the user in the Django admin panel
3. Use the token in the header of the request

```python
    resp = requests.get(
        f"{api_endpoint}/api/workflows/",
        headers={
            'Authorization': 'Token '+ naavre_api_token
        }
    )
```