# PPV Platform Monorepo

A production-ready hybrid Pay-Per-View (PPV) content platform using Django (control plane) and FastAPI (data plane).

## Architecture
- **Django**: Admin, user management, payments, token generation
- **FastAPI**: High-performance token validation, content access, signed URLs
- **PostgreSQL**: Shared DB
- **Redis**: Token cache

## Structure
- `/django_app` — Django project
- `/fastapi_app` — FastAPI service
- `/shared` — Shared utilities

## Quick Start
1. Copy `.env.example` to `/django_app/.env` and `/fastapi_app/.env` and set secrets
2. `docker-compose up --build`

---

See code for details.
