# Excel2Markdown

[![Build and Push](https://github.com/dnovichkov/Excel2Markdown/actions/workflows/build.yml/badge.svg)](https://github.com/dnovichkov/Excel2Markdown/actions/workflows/build.yml)

Web service for converting Excel files (.xls, .xlsx) to Markdown tables or JSON format.

## Features

- Convert Excel spreadsheets to Markdown tables or JSON
- Support for both .xls and .xlsx formats
- Multiple sheets converted to separate files
- Download results individually or as ZIP archive
- Asynchronous processing with progress tracking
- Clean, SEO-friendly web interface
- REST API for programmatic access
- Automatic cleanup of old files (7 days retention)

## Quick Start

### CLI (standalone)

For simple command-line usage without web server:

```bash
pip install xlrd loguru
python main.py spreadsheet.xlsx
```

This creates `.md` files for each sheet in the Excel file.

### Docker (web service)

```bash
# Clone repository
git clone https://github.com/dnovichkov/Excel2Markdown.git
cd Excel2Markdown

# Start all services
docker-compose up -d

# Open http://localhost in browser
```

## Tech Stack

- **Backend:** Python 3.11, FastAPI, Celery
- **Frontend:** Jinja2 templates, HTML/CSS/JS
- **Queue:** Redis
- **Proxy:** Nginx
- **Deployment:** Docker Compose

## Development

### Requirements

- Python 3.9+
- Redis (for Celery)

### Local Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements-dev.txt

# Start Redis (Docker)
docker run -d -p 6379:6379 redis:7-alpine

# Run FastAPI server
uvicorn app.main:app --reload

# Run Celery worker (new terminal)
celery -A app.celery_app worker --loglevel=info

# Run Celery beat (new terminal)
celery -A app.celery_app beat --loglevel=info
```

Open http://localhost:8000

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit -v

# With coverage
pytest --cov=app --cov-report=term-missing
```

## API Usage

### Start Conversion

```bash
curl -X POST http://localhost:8000/api/v1/convert \
  -F "file=@spreadsheet.xlsx" \
  -F "output_format=markdown" \
  -F "use_headers=true"
```

Response:
```json
{
  "task_id": "abc123-...",
  "status": "pending",
  "message": "Conversion to markdown started"
}
```

### Check Status

```bash
curl http://localhost:8000/api/v1/tasks/{task_id}/status
```

Response:
```json
{
  "task_id": "abc123-...",
  "status": "PROGRESS",
  "progress": 50,
  "message": "Converting sheet: Sheet2",
  "total_sheets": 3
}
```

### Download Result

```bash
curl -O http://localhost:8000/api/v1/tasks/{task_id}/download
```

## Production Deployment

See [DEPLOY.md](DEPLOY.md) for full deployment guide with:
- GitHub Actions CI/CD
- Docker Compose production setup
- SSL certificates with Let's Encrypt
- Nginx reverse proxy

### Quick Production Deploy

```bash
# On server
git clone https://github.com/dnovichkov/Excel2Markdown.git
cd Excel2Markdown

# Configure
cp .env.prod.example .env
nano .env  # Set DOMAIN and CERTBOT_EMAIL

# Initialize SSL
chmod +x scripts/init-letsencrypt.sh
./scripts/init-letsencrypt.sh

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

## Project Structure

```
Excel2Markdown/
|-- app/
|   |-- main.py              # FastAPI application
|   |-- config.py            # Configuration
|   |-- celery_app.py        # Celery setup
|   |-- api/routes/          # API endpoints
|   |-- core/                # Business logic
|   |-- services/            # Service layer
|   |-- tasks/               # Celery tasks
|   |-- templates/           # HTML templates
|   |-- static/              # CSS, JS
|-- tests/                   # Test suite
|-- docker/                  # Docker configs
|-- scripts/                 # Deployment scripts
|-- docker-compose.yml       # Development
|-- docker-compose.prod.yml  # Production
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `false` | Enable debug mode |
| `MAX_FILE_SIZE_MB` | `10` | Maximum upload size |
| `FILE_RETENTION_DAYS` | `7` | Days to keep files |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |

## License

MIT
