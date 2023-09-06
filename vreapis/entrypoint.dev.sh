#!/bin/bash

APP_PORT=${PORT:-8000}
cd /app/
/opt/venv/bin/python manage.py makemigrations
/opt/venv/bin/python manage.py migrate
/opt/venv/bin/python manage.py loaddata virtual_labs workflows catalogs data_products
/opt/venv/bin/python manage.py createsuperuser --no-input
/opt/venv/bin/python manage.py create_custom_token ${DJANGO_USERNAME} --password ${DJANGO_PASSWORD} --token ${DJANGO_TOKEN}
/opt/venv/bin/python manage.py runserver 0.0.0.0:8000