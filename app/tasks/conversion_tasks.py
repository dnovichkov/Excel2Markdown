"""Celery tasks for file conversion."""

import zipfile
from pathlib import Path
from typing import Any, Dict

from loguru import logger

from app.celery_app import celery_app
from app.config import settings
from app.core.excel_reader import get_excel_data_from_path
from app.core.markdown_converter import get_markdown_data


@celery_app.task(bind=True, name="app.tasks.conversion_tasks.convert_to_markdown")
def convert_to_markdown(
    self,
    file_path: str,
    original_filename: str,
    use_headers: bool = True,
) -> Dict[str, Any]:
    """
    Convert Excel file to Markdown format.

    Args:
        file_path: Path to the uploaded Excel file.
        original_filename: Original name of the uploaded file.
        use_headers: Whether to treat first row as headers.

    Returns:
        Dictionary with conversion result info.
    """
    task_id = self.request.id
    logger.info("Starting markdown conversion for task {}", task_id)

    try:
        # Update state: starting
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 0,
                "message": "Reading Excel file",
                "current_sheet": None,
                "total_sheets": 0,
            },
        )

        # Read Excel data
        excel_data = get_excel_data_from_path(file_path, use_headers)
        total_sheets = len(excel_data)

        logger.info("Found {} sheets in file", total_sheets)

        # Update state: processing
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 10,
                "message": f"Found {total_sheets} sheet(s)",
                "current_sheet": None,
                "total_sheets": total_sheets,
            },
        )

        # Create results directory for this task
        result_dir = settings.results_dir / task_id
        result_dir.mkdir(parents=True, exist_ok=True)

        # Convert each sheet
        results = {}
        for i, sheet in enumerate(excel_data):
            sheet_name = sheet["sheetname"]
            progress = 10 + int((i / total_sheets) * 80)

            self.update_state(
                state="PROGRESS",
                meta={
                    "progress": progress,
                    "message": f"Converting sheet: {sheet_name}",
                    "current_sheet": sheet_name,
                    "total_sheets": total_sheets,
                },
            )

            # Convert to markdown
            md_data = get_markdown_data([sheet])
            if sheet_name in md_data:
                md_content = md_data[sheet_name]
                results[sheet_name] = {
                    "content": md_content,
                    "row_count": len(sheet["data"]),
                    "column_count": len(sheet["headers"]) if sheet["headers"] else (
                        len(sheet["data"][0]) if sheet["data"] else 0
                    ),
                }

                # Save individual markdown file
                md_file_path = result_dir / f"{sheet_name}.md"
                md_file_path.write_text(md_content, encoding="utf-8")

        # Create ZIP if multiple sheets
        zip_path = None
        if len(results) > 1:
            self.update_state(
                state="PROGRESS",
                meta={
                    "progress": 95,
                    "message": "Creating ZIP archive",
                    "current_sheet": None,
                    "total_sheets": total_sheets,
                },
            )

            zip_path = result_dir / "result.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for sheet_name in results:
                    md_file = result_dir / f"{sheet_name}.md"
                    zf.write(md_file, f"{sheet_name}.md")

        logger.info("Conversion completed for task {}", task_id)

        return {
            "status": "success",
            "task_id": task_id,
            "original_filename": original_filename,
            "result_dir": str(result_dir),
            "sheets": results,
            "total_sheets": len(results),
            "has_zip": zip_path is not None,
            "zip_path": str(zip_path) if zip_path else None,
        }

    except Exception as e:
        logger.error("Conversion failed for task {}: {}", task_id, str(e))
        raise


@celery_app.task(bind=True, name="app.tasks.conversion_tasks.convert_to_json")
def convert_to_json(
    self,
    file_path: str,
    original_filename: str,
    use_headers: bool = True,
) -> Dict[str, Any]:
    """
    Convert Excel file to JSON format.

    Args:
        file_path: Path to the uploaded Excel file.
        original_filename: Original name of the uploaded file.
        use_headers: Whether to treat first row as headers.

    Returns:
        Dictionary with conversion result info.
    """
    task_id = self.request.id
    logger.info("Starting JSON conversion for task {}", task_id)

    try:
        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 0,
                "message": "Reading Excel file",
                "current_sheet": None,
                "total_sheets": 0,
            },
        )

        # Read Excel data
        excel_data = get_excel_data_from_path(file_path, use_headers)
        total_sheets = len(excel_data)

        self.update_state(
            state="PROGRESS",
            meta={
                "progress": 10,
                "message": f"Found {total_sheets} sheet(s)",
                "current_sheet": None,
                "total_sheets": total_sheets,
            },
        )

        # Create results directory
        result_dir = settings.results_dir / task_id
        result_dir.mkdir(parents=True, exist_ok=True)

        # Convert each sheet to JSON
        import json
        results = {}

        for i, sheet in enumerate(excel_data):
            sheet_name = sheet["sheetname"]
            progress = 10 + int((i / total_sheets) * 80)

            self.update_state(
                state="PROGRESS",
                meta={
                    "progress": progress,
                    "message": f"Converting sheet: {sheet_name}",
                    "current_sheet": sheet_name,
                    "total_sheets": total_sheets,
                },
            )

            # Convert to JSON records format
            headers = sheet["headers"]
            data = sheet["data"]

            if headers:
                # Create list of dictionaries
                json_data = []
                for row in data:
                    record = {}
                    for j, header in enumerate(headers):
                        key = header if header else f"column_{j}"
                        value = row[j] if j < len(row) else None
                        record[key] = value
                    json_data.append(record)
            else:
                # No headers - use list of lists
                json_data = data

            json_content = json.dumps(json_data, ensure_ascii=False, indent=2)
            results[sheet_name] = {
                "content": json_content,
                "row_count": len(data),
                "column_count": len(headers) if headers else (
                    len(data[0]) if data else 0
                ),
            }

            # Save JSON file
            json_file_path = result_dir / f"{sheet_name}.json"
            json_file_path.write_text(json_content, encoding="utf-8")

        # Create ZIP if multiple sheets
        zip_path = None
        if len(results) > 1:
            self.update_state(
                state="PROGRESS",
                meta={
                    "progress": 95,
                    "message": "Creating ZIP archive",
                    "current_sheet": None,
                    "total_sheets": total_sheets,
                },
            )

            zip_path = result_dir / "result.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for sheet_name in results:
                    json_file = result_dir / f"{sheet_name}.json"
                    zf.write(json_file, f"{sheet_name}.json")

        logger.info("JSON conversion completed for task {}", task_id)

        return {
            "status": "success",
            "task_id": task_id,
            "original_filename": original_filename,
            "result_dir": str(result_dir),
            "sheets": results,
            "total_sheets": len(results),
            "has_zip": zip_path is not None,
            "zip_path": str(zip_path) if zip_path else None,
        }

    except Exception as e:
        logger.error("JSON conversion failed for task {}: {}", task_id, str(e))
        raise
