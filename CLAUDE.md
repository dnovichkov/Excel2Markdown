# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Excel2Markdown is a web service for converting Excel files (.xls, .xlsx) to Markdown tables or JSON format. Users upload files through a web interface, conversion runs asynchronously via Celery, and results can be downloaded individually or as a ZIP archive.

## Tech Stack

- **Backend:** FastAPI + Jinja2 (SSR)
- **Background Tasks:** Celery + Redis
- **Frontend:** HTML/CSS/JS (no frameworks)
- **Reverse Proxy:** Nginx
- **Deployment:** Docker Compose

## Commands

**Development (local):**
```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run FastAPI server
uvicorn app.main:app --reload

# Run Celery worker (separate terminal)
celery -A app.celery_app worker --loglevel=info

# Run Celery beat (separate terminal)
celery -A app.celery_app beat --loglevel=info
```

**Testing:**
```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit -v

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

**Docker:**
```bash
# Build and run all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f app
docker-compose logs -f celery-worker
```

## Architecture

```
app/
|-- main.py              # FastAPI entry point
|-- config.py            # Settings (pydantic-settings)
|-- celery_app.py        # Celery configuration
|-- api/routes/          # API endpoints
|   |-- convert.py       # File upload, conversion start
|   |-- tasks.py         # Task status, result download
|   |-- health.py        # Health check
|-- core/                # Business logic
|   |-- excel_reader.py  # xlrd + openpyxl support
|   |-- markdown_converter.py
|   |-- json_converter.py
|   |-- exceptions.py
|-- services/            # Service layer
|   |-- conversion_service.py
|   |-- file_handler.py
|-- tasks/               # Celery tasks
|   |-- conversion_tasks.py
|   |-- cleanup_tasks.py  # Daily cleanup of old files
|-- templates/           # Jinja2 HTML templates
|-- static/              # CSS, JS
```

## Key Flows

**Conversion Flow:**
1. User uploads file via `/convert` (form) or `/api/v1/convert` (API)
2. File saved to `storage/uploads/{task_id}/`
3. Celery task started, returns task_id
4. Frontend polls `/api/v1/tasks/{task_id}/status`
5. Worker converts file, saves to `storage/results/{task_id}/`
6. User downloads result via `/api/v1/tasks/{task_id}/download`

**Cleanup Flow:**
- Celery Beat runs `cleanup_old_files` daily at 3:00 UTC
- Removes files older than 7 days from `storage/uploads/` and `storage/results/`

## Configuration

Environment variables (see `.env.example`):
- `DEBUG` - Enable debug mode
- `MAX_FILE_SIZE_MB` - Maximum upload size (default: 10)
- `FILE_RETENTION_DAYS` - Days to keep files (default: 7)
- `REDIS_URL` - Redis connection string
- `CELERY_BROKER_URL` - Celery broker URL
- `CELERY_RESULT_BACKEND` - Celery result backend URL

## Dependencies

**Core:**
- fastapi, uvicorn - Web framework
- celery, redis - Background tasks
- xlrd - .xls file reading
- openpyxl - .xlsx file reading
- jinja2 - Template rendering
- pydantic, pydantic-settings - Data validation
- loguru - Logging

**Dev:**
- pytest, pytest-cov - Testing
- httpx - HTTP client for tests

## CI/CD

**GitHub Actions** (`.github/workflows/build.yml`):
- Runs tests on push/PR
- Builds Docker images on push to master
- Pushes to GitHub Container Registry (ghcr.io)

**Production deployment:**
```bash
# On server: pull and restart
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

See `DEPLOY.md` for full deployment guide including SSL setup with Let's Encrypt.
