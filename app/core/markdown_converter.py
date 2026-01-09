"""Markdown conversion module for Excel data."""

from typing import Any, Dict, List, Optional

from loguru import logger

from app.core.excel_reader import SheetData


def escape_markdown_cell(value: Any) -> str:
    """
    Escape special markdown characters in cell value.

    Args:
        value: Cell value to escape.

    Returns:
        Escaped string safe for markdown table.
    """
    text = str(value) if value is not None else ""
    # Escape pipe character which is used as column separator
    text = text.replace("|", "\\|")
    # Replace newlines with <br> for multi-line content
    text = text.replace("\n", "<br>")
    return text


def get_markdown_table(
    headers: Optional[List[str]],
    data: Optional[List[List[Any]]],
) -> str:
    """
    Create markdown table from headers and data.

    Args:
        headers: List of column headers. Can be None or empty.
        data: List of rows, where each row is a list of cell values.

    Returns:
        String with table in markdown format.
    """
    result = ""

    if headers:
        escaped_headers = [escape_markdown_cell(h) for h in headers]
        result += "|" + "|".join(escaped_headers) + "|\n"
        result += "|" + "|".join(["-"] * len(headers)) + "|"
    elif data:
        # No headers but have data - create empty header row
        max_col_count = len(max(data, key=len)) if data else 0
        result += "|" + "|".join([" "] * max_col_count) + "|\n"
        result += "|" + "|".join(["-"] * max_col_count) + "|"

    if not data:
        return result

    for row in data:
        escaped_row = [escape_markdown_cell(cell) for cell in row]
        result += "\n|" + "|".join(escaped_row) + "|"

    return result


def convert_sheet_to_markdown(sheet: SheetData) -> str:
    """
    Convert a single sheet to markdown table.

    Args:
        sheet: SheetData dictionary with sheetname, headers, and data.

    Returns:
        Markdown table string.
    """
    return get_markdown_table(sheet["headers"], sheet["data"])


def get_markdown_data(excel_data: List[SheetData]) -> Dict[str, str]:
    """
    Convert all Excel sheets to markdown tables.

    Args:
        excel_data: List of SheetData dictionaries.

    Returns:
        Dictionary mapping sheet names to markdown table strings.
    """
    result: Dict[str, str] = {}

    for sheet in excel_data:
        sheetname = sheet.get("sheetname")
        if not sheetname:
            logger.warning("Empty sheetname, skipping")
            continue

        headers = sheet.get("headers")
        data = sheet.get("data")

        if not data:
            logger.warning("Empty data for sheet {}, skipping", sheetname)
            continue

        md_table = get_markdown_table(headers, data)
        result[sheetname] = md_table
        logger.debug("Converted sheet {} to markdown", sheetname)

    return result
