#!/bin/sh

# Start Django app in the background
python manage.py migrate && python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Start FastAPI app in the background
uvicorn main:app --host 0.0.0.0 --port 8001 &
FASTAPI_PID=$!

# Wait for both processes
wait $DJANGO_PID $FASTAPI_PID
