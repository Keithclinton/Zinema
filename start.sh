#!/bin/sh

# Start Django app in the background
cd ppv-platform/django_app && python manage.py migrate && python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!
cd ../../

# Start FastAPI app in the background
cd ppv-platform/fastapi_app && uvicorn main:app --host 0.0.0.0 --port 8001 &
FASTAPI_PID=$!
cd ../../

# Wait for both processes
wait $DJANGO_PID $FASTAPI_PID
