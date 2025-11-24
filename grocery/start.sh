#!/bin/bash
cd grocery
# Apply migrations
python manage.py migrate
# Start Gunicorn
gunicorn grocery.wsgi --bind 0.0.0.0:$PORT