# VREPaaS


## Development 


### Install Anaconda

Install Anaconda from these instructions: https://linuxize.com/post/how-to-install-anaconda-on-ubuntu-20-04/

Close the terminal and start a new one to activate conda.

### Create and activate conda environment

Create and activate conda environment:
```shell
conda create -n paas  python=3.9 
conda activate paas
```

#### Install tilt
Install [tilt](https://docs.tilt.dev/install.html) via conda 

```shell
conda install tilt
conda install -c conda-forge minikube 
```

#### Start Cluster

```shell
minikube start
```

#### Run tilt

```shell
tilt up
```

# Deploy Webapp
```
$make deploy-app
```


# Deploy API
```
$make deploy-api
```

# API Admin
To add/reomve resources go to: https://HOST/vre-api/admin/


