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
conda config --add channels conda-forge
conda install tilt
```

#### Run tilt
```shell
tilt up
```