"""Conversion orchestration service."""

from typing import Any, Dict, Optional

from celery.result import AsyncResult
from loguru import logger

from app.celery_app import celery_app
from app.core.exceptions import TaskNotFoundError
from app.tasks.conversion_tasks import convert_to_markdown, convert_to_json


class ConversionService:
    """Service for managing conversion tasks."""

    def start_markdown_conversion(
        self,
        file_path: str,
        original_filename: str,
        task_id: str,
        use_headers: bool = True,
    ) -> str:
        """
        Start a markdown conversion task.

        Args:
            file_path: Path to the uploaded file.
            original_filename: Original filename.
            task_id: Pre-generated task ID.
            use_headers: Whether to treat first row as headers.

        Returns:
            Task ID.
        """
        logger.info("Starting markdown conversion task: {}", task_id)

        convert_to_markdown.apply_async(
            args=[file_path, original_filename, use_headers],
            task_id=task_id,
        )

        return task_id

    def start_json_conversion(
        self,
        file_path: str,
        original_filename: str,
        task_id: str,
        use_headers: bool = True,
    ) -> str:
        """
        Start a JSON conversion task.

        Args:
            file_path: Path to the uploaded file.
            original_filename: Original filename.
            task_id: Pre-generated task ID.
            use_headers: Whether to treat first row as headers.

        Returns:
            Task ID.
        """
        logger.info("Starting JSON conversion task: {}", task_id)

        convert_to_json.apply_async(
            args=[file_path, original_filename, use_headers],
            task_id=task_id,
        )

        return task_id

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the current status of a conversion task.

        Args:
            task_id: The task ID to check.

        Returns:
            Dictionary with task status information.
        """
        result = AsyncResult(task_id, app=celery_app)

        status_info = {
            "task_id": task_id,
            "status": result.status,
            "progress": 0,
            "message": None,
            "current_sheet": None,
            "total_sheets": 0,
            "result": None,
            "error": None,
        }

        if result.status == "PENDING":
            status_info["message"] = "Task is pending"

        elif result.status == "PROGRESS":
            info = result.info or {}
            status_info["progress"] = info.get("progress", 0)
            status_info["message"] = info.get("message", "Processing")
            status_info["current_sheet"] = info.get("current_sheet")
            status_info["total_sheets"] = info.get("total_sheets", 0)

        elif result.status == "SUCCESS":
            status_info["progress"] = 100
            status_info["message"] = "Conversion completed"
            status_info["result"] = result.result

        elif result.status == "FAILURE":
            status_info["message"] = "Conversion failed"
            status_info["error"] = str(result.result) if result.result else "Unknown error"

        return status_info

    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the result of a completed task.

        Args:
            task_id: The task ID.

        Returns:
            Task result if completed, None otherwise.

        Raises:
            TaskNotFoundError: If task result is not available.
        """
        result = AsyncResult(task_id, app=celery_app)

        if result.status == "SUCCESS":
            return result.result
        elif result.status == "FAILURE":
            raise TaskNotFoundError(f"Task {task_id} failed: {result.result}")
        else:
            return None


conversion_service = ConversionService()
