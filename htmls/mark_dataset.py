import os
from bs4 import BeautifulSoup
import chardet
import re
import csv
from functools import reduce
import inspect
import types

def check_figure(soup):
    figures = soup.find_all('figure')
    correct_figures = 0
    errors = []

    for i, figure in enumerate(figures):
        if not figure.find('figcaption'):
            error_msg = f'Отсутствует тег <figcaption> внутри тега <figure> (фигура {i + 1})'
            errors.append(error_msg)
        else:
            correct_figures += 1

    return correct_figures == len(figures), errors

def check_summary_details(soup):
    summaries = soup.find_all('summary')
    errors = []

    if not summaries:
        error_msg = 'Постарайтесь использовать тэг <summary> для размещения краткого содержания или заголовка детализированного содержимого'
        errors.append(error_msg)

    return len(summaries) > 0, errors

def check_blockquote(soup):
    blockquotes = soup.find_all('blockquote')
    errors = []

    if not blockquotes:
        error_msg = 'Постарайтесь использовать тэг <blockquote> для цитирования длинных фрагментов текста из внешних источников'
        errors.append(error_msg)

    return len(blockquotes) > 0, errors

def check_cite(soup):
    cites = soup.find_all('cite')
    errors = []

    if not cites:
        error_msg = 'Постарайтесь использовать тэг <cite> для указания названия произведения или источника цитаты'
        errors.append(error_msg)

    return len(cites) > 0, errors

def check_time(soup):
    times = soup.find_all('time')
    errors = []

    if not times:
        error_msg = 'Постарайтесь использовать тэг <time> для указания даты и/или времени'
        errors.append(error_msg)

    return len(times) > 0, errors

def check_address(soup):
    addresses = soup.find_all('address')
    errors = []

    if not addresses:
        error_msg = 'Постарайтесь использовать тэг <address> для указания контактной информации автора или владельца сайта'
        errors.append(error_msg)

    return len(addresses) > 0, errors

def check_abbr(soup):
    abbrs = soup.find_all('abbr')
    correct_abbrs = 0
    errors = []

    for i, abbr in enumerate(abbrs):
        if 'title' not in abbr.attrs:
            error_msg = f'Отсутствует атрибут title в теге <abbr> (сокращение {i + 1})'
            errors.append(error_msg)
        else:
            correct_abbrs += 1

    return correct_abbrs == len(abbrs), errors

def check_q(soup):
    qs = soup.find_all('q')
    errors = []

    if not qs:
        error_msg = 'Постарайтесь использовать тэг <q> для коротких цитат с автоматическим добавлением кавычек'
        errors.append(error_msg)

    return len(qs) > 0, errors

def check_mark(soup):
    marks = soup.find_all('mark')
    errors = []

    if not marks:
        error_msg = 'Постарайтесь использовать тэг <mark> для выделения важной информации'
        errors.append(error_msg)

    return len(marks) > 0, errors

def check_del_ins(soup):
    del_ins = soup.find_all(['del', 'ins'])
    errors = []

    if not del_ins:
        error_msg = 'Постарайтесь использовать тэги <del> для удаленного текста и <ins> для вставленного текста'
        errors.append(error_msg)

    return len(del_ins) > 0, errors




def check_table(soup, file_path):
    tables = soup.find_all('table')
    errors = []
    encoding = get_encoding(file_path)

    for i, table in enumerate(tables):
        if not table.find('tr') or not (table.find('th') or table.find('td')):
            pattern = re.compile(r'<table(?:\s|>)', re.IGNORECASE)
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
                line_number = None
                for j, line in enumerate(lines):
                    if pattern.search(line):
                        line_number = j + 1
                        break
            if line_number is not None:
                error_msg = f'Неправильное использование тега <table> (строка {line_number})'
                errors.append(error_msg)

    return len(errors) == 0, errors


def check_logical_blocks(soup):
    header = soup.find('header')
    main = soup.find('main')
    footer = soup.find('footer')
    errors = []

    if not header:
        error_msg = 'Необходимо использовать тег <header> для обозначения шапки страницы'
        errors.append(error_msg)

    if not main:
        error_msg = 'Необходимо использовать тег <main> для обозначения основного контента страницы'
        errors.append(error_msg)

    if not footer:
        error_msg = 'Необходимо использовать тег <footer> для обозначения подвала страницы'
        errors.append(error_msg)

    return len(errors) == 0, errors

def check_semantic_blocks(soup):
    semantic_tags = {'nav', 'aside', 'article', 'section'}
    errors = []

    for tag in semantic_tags:
        if not soup.find(tag):
            error_msg = f'Постарайтесь использовать тег <{tag}> для разделения смысловых блоков на странице'
            errors.append(error_msg)

    return len(errors) == 0, errors

def check_headings(soup):
    headings = soup.find_all(lambda tag: tag.name.startswith('h'))
    errors = []

    if not headings:
        error_msg = 'Постарайтесь использовать тэг <h> для обозначения заголовков'
        errors.append(error_msg)

    return len(errors) == 0, errors


def check_nav_tag(soup, file_path):
    encoding = get_encoding(file_path)
    nav_tags = soup.find_all('nav')
    div_navs = soup.find_all(lambda tag: tag.name == 'div' and ('id' in tag.attrs and tag['id'] == 'nav' or 'class' in tag.attrs and 'nav' in tag['class']))

    if len(nav_tags) > 0 and len(div_navs) == 0:
        return True, []

    errors = []
    with open(file_path, 'r', encoding=encoding) as f:
        lines = f.readlines()
        for i, div in enumerate(div_navs):
            pattern = re.compile(r'<div(?:\s+(?:id|class)="nav"(?:\s+|>)|>)', re.IGNORECASE)
            line_number = None
            for j, line in enumerate(lines):
                if pattern.search(line):
                    line_number = j + 1
                    break
            if line_number is not None:
                error_msg = f'Нужно использовать nav вместо div с id/class=nav (строка {line_number})'
                errors.append(error_msg)

    return False, errors



def calculate_score(soup, file_path, criteria):
    # criteria = [
    #     check_table,
    #     check_logical_blocks,
    #     check_semantic_blocks,
    #     check_headings,
    #     check_nav_tag,
    #     check_figure,
    #     check_summary_details,
    #     check_blockquote,
    #     check_cite,
    #     check_time,
    #     check_address,
    #     check_abbr,
    #     check_q,
    #     check_mark,
    #     check_del_ins
    # ]

    total_criteria = len(criteria)
    correct_criteria = 0
    all_errors = []

    for criterion in criteria:
        is_correct, errors = criterion(soup, file_path) if isinstance(criterion, types.FunctionType) and 'file_path' in inspect.signature(criterion).parameters else criterion(soup)
        correct_criteria += is_correct
        all_errors.extend(errors)

    score = correct_criteria / total_criteria if total_criteria > 0 else 0
    return round(score, 2), all_errors




import chardet

def get_encoding(file_path):
    with open(file_path, 'rb') as f:
        rawdata = f.read()
    result = chardet.detect(rawdata)
    encoding = result.get('encoding')

    if encoding is None:
        encoding = 'utf-8'

    try:
        text = rawdata.decode(encoding)
    except UnicodeDecodeError:
        encoding = 'iso-8859-1'
        text = rawdata.decode(encoding)

    return encoding




def mark_files(directory, output_file):
    criteria = [
        check_table,
        check_logical_blocks,
        check_semantic_blocks,
        check_headings,
        check_nav_tag,
        check_figure,
        check_summary_details,
        check_blockquote,
        check_cite,
        check_time,
        check_address,
        check_abbr,
        check_q,
        check_mark,
        check_del_ins
    ]

    total_files = 0
    processed_files = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                total_files += 1

    with open(output_file, 'w', newline='', encoding='utf_8_sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['file_path', 'score', 'errors'])

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    encoding = get_encoding(file_path)
                    with open(file_path, 'r', encoding=encoding) as html_file:
                        soup = BeautifulSoup(html_file, 'html.parser')
                        score, errors = calculate_score(soup, file_path, criteria)
                        writer.writerow([file_path, score, ', '.join(errors)])
                        processed_files += 1
                        percentage = (processed_files / total_files) * 100
                        print(f'Processed {processed_files}/{total_files} files ({percentage:.2f}%)')



if __name__ == '__main__':
    html_directory = 'D:\\PycharmProjects\\backend\\htmls\\dataset\\archive'
    output_files = {
        'training': 'D:\\PycharmProjects\\backend\\htmls\\marked_dataset\\training.csv',
        'validation': 'D:\\PycharmProjects\\backend\\htmls\\marked_dataset\\validation.csv'
    }

    # Проходим по директориям training и validation
    for subdir in ['training', 'validation']:
        subdir_path = os.path.join(html_directory, subdir)
        output_file = output_files[subdir]

        # Проходим по директориям Phish и NotPhish
        for label in ['Phish', 'NotPhish']:
            label_path = os.path.join(subdir_path, label)
            mark_files(label_path, output_file)
