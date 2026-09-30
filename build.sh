#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Navigate into the subfolder where manage.py is located
cd taskmanager

python manage.py collectstatic --no-input
python manage.py migrate
