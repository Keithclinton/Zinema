FROM python:3.13-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from both apps
COPY ppv-platform/django_app/requirements.txt ./django_requirements.txt
COPY ppv-platform/fastapi_app/requirements.txt ./fastapi_requirements.txt

# Combine requirements and install
RUN cat django_requirements.txt fastapi_requirements.txt > requirements.txt \
    && pip install --no-cache-dir -r requirements.txt

# Copy all app code
COPY ppv-platform/django_app ./django_app
COPY ppv-platform/fastapi_app ./fastapi_app
COPY ppv-platform/shared ./shared
COPY ppv-platform/nginx/nginx.conf /etc/nginx/nginx.conf
COPY start.sh ./start.sh

# Make start.sh executable
RUN chmod +x ./start.sh

# Expose the public Nginx port plus the internal app ports
EXPOSE 80 8000 8001

CMD ["./start.sh"]
