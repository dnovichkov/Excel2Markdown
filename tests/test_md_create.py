import unittest
from main import get_markdown_table


class TestMarkdownCreate(unittest.TestCase):

    def test_headers_only(self):
        headers = ["Header1", "", "Header3"]
        expected_table = "|Header1||Header3|\r\n" \
                         "|-|-|-|"
        result = get_markdown_table(headers, None)
        self.assertEqual(result, expected_table)

    def test_full_table(self):
        headers = ["Header1", "Header3"]
        data = [
            [1, 2],
            [3, 4]
        ]
        expected_table = "|Header1|Header3|\r\n|-|-|\r\n|1|2|\r\n|3|4|"
        result = get_markdown_table(headers, data)
        self.assertEqual(result, expected_table)

    def test_data_only(self):
        data = [
            [1, 2],
            [3, 4]
        ]

        result = get_markdown_table(None, data)
        expected_table = "| | |\r\n|-|-|\r\n|1|2|\r\n|3|4|"
        self.assertEqual(result, expected_table)
