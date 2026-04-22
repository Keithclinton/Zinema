#!/bin/sh

# Debug: List /app contents before starting 
echo "Listing /app contents:"; ls -l /app

# Wait for Postgres to be ready (robust for cloud deploys)
echo "Waiting for Postgres at $PGHOST:$PGPORT..."
until python -c "import socket; s = socket.socket(); s.settimeout(1); s.connect(('${PGHOST}', int('${PGPORT}'))); s.close()" ; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done
echo "Postgres is up!"

# Start Django app in the background
cd /app/django_app && python manage.py migrate && gunicorn django_app.wsgi:application --bind 0.0.0.0:8000 &
DJANGO_PID=$!

# Start FastAPI app in the background
cd /app/fastapi_app && uvicorn main:app --host 0.0.0.0 --port 8001 &
FASTAPI_PID=$!

# Wait for both processes
wait $DJANGO_PID $FASTAPI_PID
