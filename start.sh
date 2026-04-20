#!/bin/sh

# Start Django app in the background
cd django_app && python manage.py migrate && gunicorn django_app.wsgi:application --bind 0.0.0.0:8000 &
DJANGO_PID=$!
cd ..

# Start FastAPI app in the background
cd fastapi_app && uvicorn main:app --host 0.0.0.0 --port 8001 &
FASTAPI_PID=$!
cd ..

# Wait for both processes
wait $DJANGO_PID $FASTAPI_PID
