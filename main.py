from loguru import logger
import argparse


def get_excel_data(excel_filename: str):
    """
    Open excel file and exctract table.
    :param excel_filename:
    :return:
    """
    result = []
    # TODO: read sheets here.
    sheets = []
    for sheet in sheets:
        sheet_name = ''
        headers = []
        data = []
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
    :param headers:
    :param data:
    :return:
    """
    # TODO: implement
    return ''


def get_markdown_data(excel_data):
    """
    Convert data to markdown tables.
    :param excel_data: List of dict in following format: [{'sheetname': 'Name of excel sheet', 'headers': [], 'data': []}]
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
    :return:
    """
    md_filenames = []
    for sheetname, md_data in data.items():
        md_filename = sheetname + '.md'
        # TODO: write file here.
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
