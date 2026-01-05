#!/bin/bash

# migrate
python src/manage.py migrate

if [ -n "$RUN_TASK" ]; then
    PYTHONPATH=src python src/manage.py $RUN_TASK
else
    PYTHONPATH=src gunicorn --timeout 300 config.wsgi:application --bind 0.0.0.0:8080
fi