"""Celery tasks for file cleanup."""

import shutil
from datetime import datetime, timedelta
from pathlib import Path

from loguru import logger

from app.celery_app import celery_app
from app.config import settings


@celery_app.task(name="app.tasks.cleanup_tasks.cleanup_old_files")
def cleanup_old_files() -> dict:
    """
    Remove files older than retention period from storage directories.

    This task is scheduled to run daily via Celery Beat.

    Returns:
        Dictionary with cleanup statistics.
    """
    max_age_days = settings.file_retention_days
    cutoff = datetime.now() - timedelta(days=max_age_days)
    cutoff_timestamp = cutoff.timestamp()

    logger.info(
        "Starting cleanup of files older than {} days (before {})",
        max_age_days,
        cutoff.isoformat(),
    )

    stats = {
        "uploads_removed": 0,
        "results_removed": 0,
        "errors": [],
    }

    directories = [
        ("uploads", settings.uploads_dir),
        ("results", settings.results_dir),
    ]

    for dir_name, dir_path in directories:
        if not dir_path.exists():
            logger.debug("Directory does not exist: {}", dir_path)
            continue

        for item in dir_path.iterdir():
            try:
                # Get modification time
                mtime = item.stat().st_mtime

                if mtime < cutoff_timestamp:
                    if item.is_dir():
                        shutil.rmtree(item)
                        logger.debug("Removed directory: {}", item)
                    else:
                        item.unlink()
                        logger.debug("Removed file: {}", item)

                    if dir_name == "uploads":
                        stats["uploads_removed"] += 1
                    else:
                        stats["results_removed"] += 1

            except Exception as e:
                error_msg = f"Failed to remove {item}: {e}"
                logger.error(error_msg)
                stats["errors"].append(error_msg)

    total_removed = stats["uploads_removed"] + stats["results_removed"]
    logger.info(
        "Cleanup completed: {} uploads removed, {} results removed",
        stats["uploads_removed"],
        stats["results_removed"],
    )

    if stats["errors"]:
        logger.warning("Cleanup had {} errors", len(stats["errors"]))

    return stats


@celery_app.task(name="app.tasks.cleanup_tasks.cleanup_task_files")
def cleanup_task_files(task_id: str) -> dict:
    """
    Remove all files associated with a specific task.

    Args:
        task_id: The task ID whose files should be removed.

    Returns:
        Dictionary with cleanup result.
    """
    logger.info("Cleaning up files for task {}", task_id)

    removed = []
    errors = []

    # Check uploads directory
    upload_dir = settings.uploads_dir / task_id
    if upload_dir.exists():
        try:
            shutil.rmtree(upload_dir)
            removed.append(str(upload_dir))
            logger.debug("Removed upload directory: {}", upload_dir)
        except Exception as e:
            errors.append(f"Failed to remove {upload_dir}: {e}")

    # Check results directory
    result_dir = settings.results_dir / task_id
    if result_dir.exists():
        try:
            shutil.rmtree(result_dir)
            removed.append(str(result_dir))
            logger.debug("Removed result directory: {}", result_dir)
        except Exception as e:
            errors.append(f"Failed to remove {result_dir}: {e}")

    return {
        "task_id": task_id,
        "removed": removed,
        "errors": errors,
    }
