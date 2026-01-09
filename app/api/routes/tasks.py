"""Task status and result endpoints."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.schemas.response import TaskStatusResponse, SheetResult, ConversionResultResponse
from app.services.conversion_service import conversion_service
from app.services.file_handler import file_handler

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """
    Get the current status of a conversion task.

    Args:
        task_id: The task ID to check.

    Returns:
        Task status information including progress.
    """
    status = conversion_service.get_task_status(task_id)
    return TaskStatusResponse(**status)


@router.get("/{task_id}/result", response_model=ConversionResultResponse)
async def get_task_result(task_id: str) -> ConversionResultResponse:
    """
    Get the full result of a completed conversion task.

    Args:
        task_id: The task ID.

    Returns:
        Full conversion result with all sheet contents.

    Raises:
        HTTPException: If task is not found or not completed.
    """
    result = conversion_service.get_task_result(task_id)

    if result is None:
        status = conversion_service.get_task_status(task_id)
        if status["status"] == "FAILURE":
            raise HTTPException(
                status_code=500,
                detail=f"Task failed: {status.get('error', 'Unknown error')}",
            )
        raise HTTPException(
            status_code=202,
            detail="Task is still processing",
        )

    sheets = []
    for sheet_name, sheet_data in result.get("sheets", {}).items():
        sheets.append(
            SheetResult(
                sheet_name=sheet_name,
                content=sheet_data["content"],
                row_count=sheet_data["row_count"],
                column_count=sheet_data["column_count"],
            )
        )

    return ConversionResultResponse(
        task_id=task_id,
        status="success",
        original_filename=result.get("original_filename", ""),
        sheets=sheets,
        total_sheets=result.get("total_sheets", len(sheets)),
        has_zip=result.get("has_zip", False),
    )


@router.get("/{task_id}/download")
async def download_result(task_id: str, file: str = None):
    """
    Download conversion result file.

    Args:
        task_id: The task ID.
        file: Optional specific filename to download.
              If not provided, downloads ZIP (if available) or single file.

    Returns:
        File download response.

    Raises:
        HTTPException: If file is not found.
    """
    result = conversion_service.get_task_result(task_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Task result not found")

    try:
        if file:
            # Download specific file
            file_path = file_handler.get_result_file(task_id, file)
            return FileResponse(
                path=file_path,
                filename=file,
                media_type="application/octet-stream",
            )

        # Download ZIP if available, otherwise single file
        if result.get("has_zip"):
            zip_path = file_handler.get_result_zip(task_id)
            original_name = Path(result.get("original_filename", "result")).stem
            return FileResponse(
                path=zip_path,
                filename=f"{original_name}.zip",
                media_type="application/zip",
            )

        # Single file - find and download it
        files = file_handler.list_result_files(task_id)
        files = [f for f in files if f != "result.zip"]

        if not files:
            raise HTTPException(status_code=404, detail="No result files found")

        file_path = file_handler.get_result_file(task_id, files[0])
        return FileResponse(
            path=file_path,
            filename=files[0],
            media_type="application/octet-stream",
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
