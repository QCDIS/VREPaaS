FROM python:3.9.7-slim

COPY ./vreapis /app
WORKDIR /app

RUN python3 -m venv /opt/venv

RUN /opt/venv/bin/pip install pip --upgrade && \
    /opt/venv/bin/pip install -r requirements.txt && \
    chmod +x entrypoint.dev.sh

CMD ["/app/entrypoint.dev.sh"]