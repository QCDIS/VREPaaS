#!/bin/bash

APP_PORT=${PORT:-8000}
cd /app/
/opt/venv/bin/python manage.py collectstatic --no-input
/opt/venv/bin/python manage.py wait_for_database
/opt/venv/bin/python manage.py makemigrations
/opt/venv/bin/python manage.py migrate
/opt/venv/bin/python manage.py createsuperuser --no-input
/opt/venv/bin/python manage.py create_custom_token ${DJANGO_USERNAME} --password ${DJANGO_PASSWORD} --token ${DJANGO_TOKEN}
/opt/venv/bin/gunicorn --worker-tmp-dir /dev/shm vreapis.wsgi:application --bind "0.0.0.0:${APP_PORT}"