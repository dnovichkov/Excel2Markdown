"""Health check endpoint."""

from fastapi import APIRouter

from app.config import settings
from app.schemas.response import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check application health.

    Returns:
        Health status and version information.
    """
    return HealthResponse(
        status="ok",
        version=settings.app_version,
    )
