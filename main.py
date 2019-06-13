import argparse

from loguru import logger
from xlrd import open_workbook


def get_excel_data(excel_filename: str, use_headers: bool = True):
    """
    Open excel file and exctract table.
    :param excel_filename:
    :param use_headers:
    :return:
    """
    result = []
    xl_workbook = open_workbook(excel_filename)
    sheet_names = xl_workbook.sheet_names()

    for sheet_name in sheet_names:
        xl_sheet = xl_workbook.sheet_by_name(sheet_name)
        num_cols = xl_sheet.ncols
        headers = []
        data = []
        start_row_idx = 0
        if use_headers and xl_sheet.nrows:
            start_row_idx = 1
            for col_idx in range(0, num_cols):
                cell_obj = xl_sheet.cell(0, col_idx)
                headers.append(cell_obj.value)
        for row_idx in range(start_row_idx, xl_sheet.nrows):
            row_data = []
            for col_idx in range(0, num_cols):
                cell_obj = xl_sheet.cell(row_idx, col_idx)
                row_data.append(cell_obj.value)
            data.append(row_data)

        result.append(
            {
                'sheetname': sheet_name,
                'headers': headers,
                'data': data
            }
        )

    return result


def get_markdown_table(headers, data):
    """
    Create markdown table
    :param headers: List of table headers
    :param data: List with table data: [[Row1Col1, Row1Col2], [Row2Col1, Row2Col2]]
    :return: string with table in markdown format.
    """
    res = ''

    if headers:
        res += '|' + '|'.join(headers) + '|\n'
        res += '|' + '|'.join(['-'] * len(headers)) + '|'
    elif data:
        max_col_count = len(max(data, key=len))
        res += '|' + '|'.join([' '] * max_col_count) + '|\n'
        res += '|' + '|'.join(['-'] * max_col_count) + '|'
    if not data:
        return res
    for rec in data:
        res += '\n|' + '|'.join(map(str, rec)) + '|'

    return res


def get_markdown_data(excel_data):
    """
    Convert data to markdown tables.
    :param excel_data: List of dict in following format:
        [{'sheetname': 'Name of excel sheet', 'headers': [], 'data': []}]
    :return: dict with md sheet_name and md_table.
    """
    result = {}
    for rec in excel_data:
        sheetname = rec.get('sheetname')
        if not sheetname:
            logger.warning('Empty sheetname')
            continue
        headers = rec.get('headers')
        data = rec.get('data')
        if not data:
            logger.warning('Empty data for sheet {}', sheetname)
            continue
        md_data = get_markdown_table(headers, data)
        result[sheetname] = md_data
    return result


def save_to_markdown_files(data):
    """
    Save data to md-files with table.
    :param data: Dict in following format: {sheet_name: md_data}.
    :return: list with name of created files.
    """
    md_filenames = []
    for sheetname, md_data in data.items():
        md_filename = sheetname + '.md'
        with open(md_filename, "w") as f:
            f.write(md_data)
        md_filenames.append(md_filename)
    return md_filenames


def __main():
    logger.info("It is CLI-program for extracting Excel-tables to md-files")
    parser = argparse.ArgumentParser(description='Converting Excel to mdf')
    parser.add_argument('excel_filename', type=str,
                        help='An excel-table filename')
    args = parser.parse_args()
    excel_filename = args.excel_filename
    if not excel_filename:
        logger.error('It is neccessary to provide excel filename')
        return
    logger.info("Excel file is {}", excel_filename)

    excel_data = get_excel_data(excel_filename)
    md_data = get_markdown_data(excel_data)
    files = save_to_markdown_files(md_data)
    logger.info('Saved to {}', files)


if __name__ == "__main__":
    __main()
