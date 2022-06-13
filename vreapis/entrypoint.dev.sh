#!/bin/bash

APP_PORT=${PORT:-8000}
cd /app/
/opt/venv/bin/python manage.py runserver