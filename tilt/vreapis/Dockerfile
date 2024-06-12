# FROM python:3.12.2-slim
FROM python:3.11.9-slim
# Dependency pytype [used by PyExtractor] complains 'Python versions > 3.11 are not yet supported'

WORKDIR /app

RUN apt update && \
    apt install -y libpq-dev gcc gdal-bin curl net-tools iputils-ping r-base

# Install rysnc for Tilt syncback
RUN apt install -y rsync

RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install pip --upgrade

COPY ./vreapis/requirements.txt /app
RUN /opt/venv/bin/pip install -r requirements.txt

# Set another directory for installation of R packages to avoid permission problem
# RUN echo 'R_LIBS_USER="~/R/library"' >> ~/.Renviron

COPY ./vreapis /app
RUN chmod +x entrypoint.dev.sh

CMD ["/app/entrypoint.dev.sh"]
