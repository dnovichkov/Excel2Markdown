"""Pytest configuration and fixtures for Excel2Markdown tests."""

import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_xlsx_path(fixtures_dir: Path) -> Path:
    """Return path to sample .xlsx test file."""
    return fixtures_dir / "sample.xlsx"


@pytest.fixture
def sample_sheet_data():
    """Return sample SheetData for testing."""
    return {
        "sheetname": "TestSheet",
        "headers": ["Header1", "Header2"],
        "data": [
            [1, 2],
            ["a", "b"],
        ],
    }


@pytest.fixture
def sample_sheet_data_no_headers():
    """Return sample SheetData without headers."""
    return {
        "sheetname": "TestSheet",
        "headers": [],
        "data": [
            [1, 2],
            ["a", "b"],
        ],
    }


@pytest.fixture
def multi_sheet_data():
    """Return sample data with multiple sheets."""
    return [
        {
            "sheetname": "Sheet1",
            "headers": ["Col1", "Col2"],
            "data": [[1, 2], [3, 4]],
        },
        {
            "sheetname": "Sheet2",
            "headers": ["Name", "Value"],
            "data": [["test", 100]],
        },
    ]
