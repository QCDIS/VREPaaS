#!/bin/bash

APP_PORT=${PORT:-8000}
cd /app/
/opt/venv/bin/python manage.py makemigrations
/opt/venv/bin/python manage.py migrate
/opt/venv/bin/python manage.py loaddata virtual_labs
/opt/venv/bin/python manage.py createsuperuser --no-input
/opt/venv/bin/python manage.py runserver