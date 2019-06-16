import unittest
from main import get_markdown_data


class TestMarkdownGet(unittest.TestCase):

    def test_empty(self):
        empty_excel_data = []
        result = get_markdown_data(empty_excel_data)
        self.assertEqual(result, {})

    def test_one_sheet_only(self):
        excel_data = [{'sheetname': 'TestSheet'}]
        expected_result = {}
        result = get_markdown_data(excel_data)
        self.assertEqual(result, expected_result)

    def test_one_sheet_with_data_and_headers(self):
        excel_data = [
            {
                'sheetname': 'TestSheet',
                'headers': ['Header1', 'Header 2'],
                'data': [
                    [1, 2],
                    ['a', 'b']
                ]
            }
        ]
        expected_result = {'TestSheet': "|Header1|Header 2|\n|-|-|\n|1|2|\n|a|b|"}
        result = get_markdown_data(excel_data)
        self.assertEqual(result, expected_result)

    def test_one_sheet_with_data_only(self):
        excel_data = [
            {
                'sheetname': 'TestSheet',
                'data': [
                    [1, 2],
                    ['a', 'b']
                ]
            }
        ]
        expected_result = {'TestSheet': "| | |\n|-|-|\n|1|2|\n|a|b|"}
        result = get_markdown_data(excel_data)
        self.assertEqual(result, expected_result)

    def test_one_sheet_with_headers_only(self):
        excel_data = [
            {
                'sheetname': 'TestSheet',
                'headers': ['Header1', 'Header 2'],
            }
        ]
        expected_result = {}
        result = get_markdown_data(excel_data)
        self.assertEqual(result, expected_result)
