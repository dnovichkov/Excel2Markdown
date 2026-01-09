"""Response schemas for API endpoints."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str


class TaskCreatedResponse(BaseModel):
    """Response when a conversion task is created."""

    task_id: str
    status: str = "pending"
    message: str = "Conversion task created"


class TaskStatusResponse(BaseModel):
    """Response for task status polling."""

    task_id: str
    status: Literal["PENDING", "PROGRESS", "SUCCESS", "FAILURE"]
    progress: int = Field(default=0, ge=0, le=100)
    message: Optional[str] = None
    current_sheet: Optional[str] = None
    total_sheets: int = 0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SheetResult(BaseModel):
    """Result for a single sheet conversion."""

    sheet_name: str
    content: str
    row_count: int
    column_count: int


class ConversionResultResponse(BaseModel):
    """Full conversion result response."""

    task_id: str
    status: str
    original_filename: str
    sheets: List[SheetResult]
    total_sheets: int
    has_zip: bool = False


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    detail: Optional[str] = None
    error_type: Optional[str] = None
