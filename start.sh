#!/bin/bash
set -e

# Add /app to PYTHONPATH so imports of 'shared' module work from django_app and fastapi_app
export PYTHONPATH=/app:$PYTHONPATH

# Extract database host and port from DATABASE_URL or fall back to env vars
if [ -n "$DATABASE_URL" ]; then
  DB_HOST=$(python3 -c "from urllib.parse import urlparse; u = urlparse('$DATABASE_URL'); print(u.hostname or 'localhost')")
  DB_PORT=$(python3 -c "from urllib.parse import urlparse; u = urlparse('$DATABASE_URL'); print(u.port or 5432)")
else
  DB_HOST=${PGHOST:-${DB_HOST:-localhost}}
  DB_PORT=${PGPORT:-${DB_PORT:-5432}}
fi

echo "Waiting for Postgres at $DB_HOST:$DB_PORT..."
for i in $(seq 1 30); do
  if python3 -c "import socket; s = socket.socket(); s.settimeout(1); s.connect(('$DB_HOST', int($DB_PORT))); s.close()" 2>/dev/null; then
    echo "Postgres is up!"
    break
  fi
  echo "Postgres is unavailable (attempt $i/30) - sleeping"
  sleep 2
done

# Start Django app in the background
cd /app/django_app && python manage.py migrate && gunicorn django_app.wsgi:application --bind 0.0.0.0:8000 &
DJANGO_PID=$!

# Start FastAPI app in the background
cd /app/fastapi_app && uvicorn main:app --host 0.0.0.0 --port 8001 &
FASTAPI_PID=$!

# Run Nginx in the foreground as the public entrypoint
nginx -g 'daemon off;'
