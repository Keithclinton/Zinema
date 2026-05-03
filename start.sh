#!/bin/sh

# Debug: List /app contents before starting 
echo "Listing /app contents:"; ls -l /app



DB_HOST_NAME=$(python -c "import os; from urllib.parse import urlparse; url = os.getenv('DATABASE_URL'); print(urlparse(url).hostname if url and urlparse(url).hostname else os.getenv('PGHOST', os.getenv('DB_HOST', 'zinema.railway.internal')))" )
DB_PORT_NUMBER=$(python -c "import os; from urllib.parse import urlparse; url = os.getenv('DATABASE_URL'); print(urlparse(url).port if url and urlparse(url).port else os.getenv('PGPORT', os.getenv('DB_PORT', '5432')))" )

echo "Waiting for Postgres at $DB_HOST_NAME:$DB_PORT_NUMBER..."
until python -c "import socket; s = socket.socket(); s.settimeout(1); s.connect(('$DB_HOST_NAME', int('$DB_PORT_NUMBER'))); s.close()" ; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done
echo "Postgres is up! Moving to migrations..."
echo "Postgres is up!"

# Start Django app in the background
cd /app/django_app && python manage.py migrate && gunicorn django_app.wsgi:application --bind 0.0.0.0:8000 &
DJANGO_PID=$!

# Start FastAPI app in the background
cd /app/fastapi_app && uvicorn main:app --host 0.0.0.0 --port 8001 &
FASTAPI_PID=$!

# Run Nginx in the foreground as the public entrypoint
nginx -g 'daemon off;'
