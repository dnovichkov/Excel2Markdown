"""FastAPI application entry point."""

from pathlib import Path
from urllib.parse import unquote

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from app.api.routes import convert, health, tasks
from app.config import settings
from app.core.exceptions import Excel2MarkdownError
from app.services.conversion_service import conversion_service

# Application setup
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Convert Excel files to Markdown or JSON format",
)

# Static files and templates
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Include routers
app.include_router(health.router)
app.include_router(convert.router)
app.include_router(tasks.router)


# Exception handlers
@app.exception_handler(Excel2MarkdownError)
async def excel_error_handler(request: Request, exc: Excel2MarkdownError):
    """Handle Excel2Markdown specific errors."""
    accept = request.headers.get("accept", "")

    if "application/json" in accept:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=400,
            content={
                "error": str(exc),
                "error_type": exc.__class__.__name__,
            },
        )

    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
        },
        status_code=400,
    )


# Page routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main upload page."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "max_file_size_mb": settings.max_file_size_mb,
            "allowed_extensions": settings.allowed_extensions,
        },
    )


@app.get("/progress/{task_id}", response_class=HTMLResponse)
async def progress_page(request: Request, task_id: str):
    """Render the progress tracking page."""
    return templates.TemplateResponse(
        "progress.html",
        {
            "request": request,
            "task_id": task_id,
        },
    )


@app.get("/result/{task_id}", response_class=HTMLResponse)
async def result_page(request: Request, task_id: str):
    """Render the conversion result page."""
    result = conversion_service.get_task_result(task_id)

    if result is None:
        # Task not complete, redirect to progress
        return RedirectResponse(url=f"/progress/{task_id}")

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "task_id": task_id,
            "result": result,
        },
    )


@app.get("/error", response_class=HTMLResponse)
async def error_page(request: Request, message: str = "An error occurred"):
    """Render the error page."""
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error": unquote(message),
        },
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting {} v{}", settings.app_name, settings.app_version)

    # Ensure storage directories exist
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.results_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Storage directories initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down {}", settings.app_name)
