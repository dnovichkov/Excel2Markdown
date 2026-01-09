"""Unit tests for excel reader module."""

import pytest
from io import BytesIO

from app.core.excel_reader import (
    detect_excel_format,
    get_excel_data,
)
from app.core.exceptions import InvalidFileFormatError


class TestDetectExcelFormat:
    """Tests for detect_excel_format function."""

    def test_xls_format(self):
        assert detect_excel_format("test.xls") == "xls"

    def test_xlsx_format(self):
        assert detect_excel_format("test.xlsx") == "xlsx"

    def test_uppercase_extension(self):
        assert detect_excel_format("test.XLS") == "xls"
        assert detect_excel_format("test.XLSX") == "xlsx"

    def test_mixed_case_extension(self):
        assert detect_excel_format("test.Xlsx") == "xlsx"

    def test_invalid_format_txt(self):
        with pytest.raises(InvalidFileFormatError) as exc_info:
            detect_excel_format("test.txt")
        assert ".txt" in str(exc_info.value)

    def test_invalid_format_csv(self):
        with pytest.raises(InvalidFileFormatError):
            detect_excel_format("data.csv")

    def test_no_extension(self):
        with pytest.raises(InvalidFileFormatError):
            detect_excel_format("filename")

    def test_path_with_directories(self):
        assert detect_excel_format("/path/to/file.xlsx") == "xlsx"
        assert detect_excel_format("C:\\Users\\test\\file.xls") == "xls"


class TestGetExcelData:
    """Tests for get_excel_data function with real file content."""

    def test_invalid_file_content(self):
        """Test that invalid content raises appropriate error."""
        with pytest.raises(InvalidFileFormatError):
            get_excel_data(b"not excel content", "test.xlsx")

    def test_invalid_format_extension(self):
        """Test that unsupported extension raises error."""
        with pytest.raises(InvalidFileFormatError):
            get_excel_data(b"content", "test.csv")
