"""File upload and download handling service."""

import uuid
from pathlib import Path
from typing import BinaryIO, Tuple

from fastapi import UploadFile
from loguru import logger

from app.config import settings
from app.core.exceptions import FileTooLargeError, InvalidFileFormatError


class FileHandler:
    """Service for handling file uploads and downloads."""

    def __init__(self):
        """Initialize file handler and ensure storage directories exist."""
        settings.uploads_dir.mkdir(parents=True, exist_ok=True)
        settings.results_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file.

        Args:
            file: The uploaded file to validate.

        Raises:
            InvalidFileFormatError: If file extension is not allowed.
            FileTooLargeError: If file exceeds size limit.
        """
        if not file.filename:
            raise InvalidFileFormatError("Filename is required")

        # Check extension
        ext = Path(file.filename).suffix.lower()
        if ext not in settings.allowed_extensions:
            raise InvalidFileFormatError(
                f"File type {ext} is not allowed. "
                f"Supported formats: {', '.join(settings.allowed_extensions)}"
            )

        # Check file size if available
        if file.size and file.size > settings.max_file_size_bytes:
            raise FileTooLargeError(
                f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB"
            )

    async def save_upload(
        self,
        file: UploadFile,
        task_id: str,
    ) -> Tuple[Path, str]:
        """
        Save uploaded file to storage.

        Args:
            file: The uploaded file.
            task_id: Task ID to associate with the file.

        Returns:
            Tuple of (file_path, original_filename).
        """
        if not file.filename:
            raise InvalidFileFormatError("Filename is required")

        # Create task-specific upload directory
        upload_dir = settings.uploads_dir / task_id
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Save file with original name
        file_path = upload_dir / file.filename
        content = await file.read()

        # Additional size check after reading
        if len(content) > settings.max_file_size_bytes:
            raise FileTooLargeError(
                f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB"
            )

        file_path.write_bytes(content)
        logger.info("Saved uploaded file: {}", file_path)

        return file_path, file.filename

    def get_result_file(self, task_id: str, filename: str) -> Path:
        """
        Get path to a result file.

        Args:
            task_id: Task ID.
            filename: Name of the result file.

        Returns:
            Path to the result file.

        Raises:
            FileNotFoundError: If file does not exist.
        """
        file_path = settings.results_dir / task_id / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Result file not found: {filename}")
        return file_path

    def get_result_zip(self, task_id: str) -> Path:
        """
        Get path to the ZIP archive for a task.

        Args:
            task_id: Task ID.

        Returns:
            Path to the ZIP file.

        Raises:
            FileNotFoundError: If ZIP does not exist.
        """
        zip_path = settings.results_dir / task_id / "result.zip"
        if not zip_path.exists():
            raise FileNotFoundError("ZIP archive not found")
        return zip_path

    def list_result_files(self, task_id: str) -> list:
        """
        List all result files for a task.

        Args:
            task_id: Task ID.

        Returns:
            List of filenames in the result directory.
        """
        result_dir = settings.results_dir / task_id
        if not result_dir.exists():
            return []
        return [f.name for f in result_dir.iterdir() if f.is_file()]

    @staticmethod
    def generate_task_id() -> str:
        """Generate a unique task ID."""
        return str(uuid.uuid4())


file_handler = FileHandler()
