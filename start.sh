#!/bin/bash

# Apply migrations
python manage.py migrate

# Start Gunicorn server
gunicorn grocery.grocery.wsgi --bind 0.0.0.0:$PORT
