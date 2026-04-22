#!/bin/sh

# Debug: List /app contents before starting 
echo "Listing /app contents:"; ls -l /app

# Wait for Postgres to be ready (robust for cloud deploys)
echo "Waiting for database host '$PGHOST'..."
while ! nc -z "$PGHOST" "$PGPORT"; do
	echo "Waiting for Postgres at $PGHOST:$PGPORT..."
	sleep 1
done

# Start Django app in the background
python /app/django_app/manage.py migrate && \
gunicorn django_app.wsgi:application --chdir /app/django_app --bind 0.0.0.0:8000 &
DJANGO_PID=$!

# Start FastAPI app in the background
uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8001 --app-dir /app &
FASTAPI_PID=$!

# Wait for both processes
wait $DJANGO_PID $FASTAPI_PID
