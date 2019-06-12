import unittest
from main import get_markdown_table


class TestMarkdownCreate(unittest.TestCase):

    def test_headers_only(self):
        headers = ["Header1", "", "Header3"]
        expected_table = "| Header1|| Column 3 |" \
                         "|-|-|-|"
        self.assertEqual(headers, )
