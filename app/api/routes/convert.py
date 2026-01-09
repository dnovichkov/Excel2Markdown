"""Conversion API endpoints."""

from typing import Literal

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse

from app.core.exceptions import FileTooLargeError, InvalidFileFormatError
from app.schemas.response import TaskCreatedResponse, ErrorResponse
from app.services.conversion_service import conversion_service
from app.services.file_handler import file_handler

router = APIRouter(tags=["conversion"])


@router.post(
    "/convert",
    response_class=RedirectResponse,
    responses={
        302: {"description": "Redirect to progress page"},
        400: {"model": ErrorResponse},
    },
)
async def convert_form(
    request: Request,
    file: UploadFile = File(...),
    use_headers: bool = Form(default=True),
    output_format: Literal["markdown", "json"] = Form(default="markdown"),
):
    """
    Handle form submission for file conversion.

    Redirects to progress page after starting the conversion task.

    Args:
        file: The uploaded Excel file.
        use_headers: Whether to treat first row as headers.
        output_format: Output format (markdown or json).

    Returns:
        Redirect to progress page.
    """
    try:
        # Validate file
        file_handler.validate_file(file)

        # Generate task ID
        task_id = file_handler.generate_task_id()

        # Save uploaded file
        file_path, original_filename = await file_handler.save_upload(file, task_id)

        # Start conversion task
        if output_format == "json":
            conversion_service.start_json_conversion(
                str(file_path),
                original_filename,
                task_id,
                use_headers,
            )
        else:
            conversion_service.start_markdown_conversion(
                str(file_path),
                original_filename,
                task_id,
                use_headers,
            )

        # Redirect to progress page
        return RedirectResponse(
            url=f"/progress/{task_id}",
            status_code=302,
        )

    except (InvalidFileFormatError, FileTooLargeError) as e:
        # For form submission, redirect to error page
        return RedirectResponse(
            url=f"/error?message={str(e)}",
            status_code=302,
        )


@router.post(
    "/api/v1/convert",
    response_model=TaskCreatedResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
    },
)
async def convert_api(
    file: UploadFile = File(...),
    use_headers: bool = Form(default=True),
    output_format: Literal["markdown", "json"] = Form(default="markdown"),
) -> TaskCreatedResponse:
    """
    API endpoint for file conversion.

    Returns task ID for polling status.

    Args:
        file: The uploaded Excel file.
        use_headers: Whether to treat first row as headers.
        output_format: Output format (markdown or json).

    Returns:
        Task creation response with task ID.

    Raises:
        HTTPException: If file validation fails.
    """
    try:
        # Validate file
        file_handler.validate_file(file)

        # Generate task ID
        task_id = file_handler.generate_task_id()

        # Save uploaded file
        file_path, original_filename = await file_handler.save_upload(file, task_id)

        # Start conversion task
        if output_format == "json":
            conversion_service.start_json_conversion(
                str(file_path),
                original_filename,
                task_id,
                use_headers,
            )
        else:
            conversion_service.start_markdown_conversion(
                str(file_path),
                original_filename,
                task_id,
                use_headers,
            )

        return TaskCreatedResponse(
            task_id=task_id,
            status="pending",
            message=f"Conversion to {output_format} started",
        )

    except InvalidFileFormatError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileTooLargeError as e:
        raise HTTPException(status_code=413, detail=str(e))
