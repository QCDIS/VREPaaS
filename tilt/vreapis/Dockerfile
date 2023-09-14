FROM python:3.11.5-slim

WORKDIR /app

RUN apt update && \
    apt install -y libpq-dev gcc gdal-bin curl net-tools iputils-ping

RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install pip --upgrade

COPY ./vreapis/requirements.txt /app
RUN /opt/venv/bin/pip install -r requirements.txt

COPY ./vreapis /app
RUN chmod +x entrypoint.dev.sh

CMD ["/app/entrypoint.dev.sh"]
