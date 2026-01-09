"""Unit tests for markdown converter module."""

import pytest

from app.core.markdown_converter import (
    escape_markdown_cell,
    get_markdown_table,
    get_markdown_data,
    convert_sheet_to_markdown,
)


class TestEscapeMarkdownCell:
    """Tests for escape_markdown_cell function."""

    def test_plain_text(self):
        assert escape_markdown_cell("hello") == "hello"

    def test_pipe_character(self):
        assert escape_markdown_cell("a|b") == "a\\|b"

    def test_newline(self):
        assert escape_markdown_cell("line1\nline2") == "line1<br>line2"

    def test_none_value(self):
        assert escape_markdown_cell(None) == ""

    def test_numeric_value(self):
        assert escape_markdown_cell(42) == "42"

    def test_float_value(self):
        assert escape_markdown_cell(3.14) == "3.14"


class TestGetMarkdownTable:
    """Tests for get_markdown_table function."""

    def test_headers_only(self):
        headers = ["Header1", "", "Header3"]
        expected = "|Header1||Header3|\n|-|-|-|"
        result = get_markdown_table(headers, None)
        assert result == expected

    def test_full_table(self):
        headers = ["Header1", "Header3"]
        data = [[1, 2], [3, 4]]
        expected = "|Header1|Header3|\n|-|-|\n|1|2|\n|3|4|"
        result = get_markdown_table(headers, data)
        assert result == expected

    def test_data_only(self):
        data = [[1, 2], [3, 4]]
        expected = "| | |\n|-|-|\n|1|2|\n|3|4|"
        result = get_markdown_table(None, data)
        assert result == expected

    def test_empty_data(self):
        headers = ["Col1", "Col2"]
        result = get_markdown_table(headers, [])
        expected = "|Col1|Col2|\n|-|-|"
        assert result == expected

    def test_no_headers_no_data(self):
        result = get_markdown_table(None, None)
        assert result == ""

    def test_special_characters_escaped(self):
        headers = ["Name"]
        data = [["value|with|pipes"]]
        result = get_markdown_table(headers, data)
        assert "\\|" in result

    def test_multiline_content(self):
        headers = ["Description"]
        data = [["line1\nline2"]]
        result = get_markdown_table(headers, data)
        assert "<br>" in result


class TestGetMarkdownData:
    """Tests for get_markdown_data function."""

    def test_empty_input(self):
        result = get_markdown_data([])
        assert result == {}

    def test_sheet_without_data(self):
        excel_data = [{"sheetname": "TestSheet"}]
        result = get_markdown_data(excel_data)
        assert result == {}

    def test_sheet_with_headers_only(self):
        excel_data = [
            {
                "sheetname": "TestSheet",
                "headers": ["Header1", "Header2"],
            }
        ]
        result = get_markdown_data(excel_data)
        assert result == {}

    def test_single_sheet_with_data(self):
        excel_data = [
            {
                "sheetname": "TestSheet",
                "headers": ["Header1", "Header 2"],
                "data": [[1, 2], ["a", "b"]],
            }
        ]
        expected = {"TestSheet": "|Header1|Header 2|\n|-|-|\n|1|2|\n|a|b|"}
        result = get_markdown_data(excel_data)
        assert result == expected

    def test_single_sheet_data_only(self):
        excel_data = [
            {
                "sheetname": "TestSheet",
                "data": [[1, 2], ["a", "b"]],
            }
        ]
        expected = {"TestSheet": "| | |\n|-|-|\n|1|2|\n|a|b|"}
        result = get_markdown_data(excel_data)
        assert result == expected

    def test_multiple_sheets(self, multi_sheet_data):
        result = get_markdown_data(multi_sheet_data)
        assert len(result) == 2
        assert "Sheet1" in result
        assert "Sheet2" in result

    def test_empty_sheetname_skipped(self):
        excel_data = [
            {
                "sheetname": "",
                "headers": ["Col1"],
                "data": [[1]],
            }
        ]
        result = get_markdown_data(excel_data)
        assert result == {}


class TestConvertSheetToMarkdown:
    """Tests for convert_sheet_to_markdown function."""

    def test_with_headers_and_data(self, sample_sheet_data):
        result = convert_sheet_to_markdown(sample_sheet_data)
        assert "|Header1|Header2|" in result
        assert "|1|2|" in result

    def test_without_headers(self, sample_sheet_data_no_headers):
        result = convert_sheet_to_markdown(sample_sheet_data_no_headers)
        assert "| | |" in result
        assert "|1|2|" in result
