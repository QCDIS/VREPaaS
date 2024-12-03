# FROM python:3.12.2-slim
FROM python:3.11.9-slim

WORKDIR /app

RUN apt update && \
    apt install -y libpq-dev gcc gdal-bin curl net-tools iputils-ping r-base

RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install pip --upgrade

COPY ./requirements.txt /app
RUN /opt/venv/bin/pip install -r requirements.txt

RUN Rscript -e "install.packages(c('rlang', 'lobstr', 'purrr', 'renv'), repos = 'https://cloud.r-project.org')"

COPY . /app
RUN chmod +x entrypoint.sh

CMD ["/app/entrypoint.sh"]
