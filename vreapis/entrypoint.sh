#!/bin/bash

APP_PORT=${PORT:-8000}
cd /app/
/opt/venv/bin/python manage.py collectstatic --no-input
/opt/venv/bin/python manage.py makemigrations
/opt/venv/bin/python manage.py migrate
/opt/venv/bin/python manage.py loaddata virtual_labs catalogs
/opt/venv/bin/python manage.py createsuperuser --no-input
/opt/venv/bin/gunicorn --worker-tmp-dir /dev/shm vreapis.wsgi:application --bind "0.0.0.0:${APP_PORT}"