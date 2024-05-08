from bs4 import BeautifulSoup
import chardet
import re
import inspect
import types



def extract_contact_info(html):
    # Регулярные выражения для поиска телефона, email и адреса
    phone_regex = r'(?:\+?(\d[\d\s()]*)?(\([\d\s()]+\))?[\d\s()-]+\d|\+?7?\s?\(?(\d{3})\)?[-.\s]?\d{3}[-.\s]?\d{2}[-.\s]?\d{2})'
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    address_regex = r'(?:\d{1,4}[\s.,-]?[\w\s.,-]{2,}(?:street|st|avenue|ave|road|rd|highway|hwy|square|sq|trail|trl|drive|dr|court|ct|park|pk|lane|ln|boulevard|blvd|circle|cir|plaza|plz|alley|aly|way|wy|point|pt|parkway|pkwy|commune|cm|district|dist|province|prov|region|reg|territory|terr|city|cty|town|tn|village|vlg|municipality|mun|county|cnty|state|st|country|cntry|ул|пр|просп|пер|ш|шоссе|бульв|бульвар|наб|набережн|пл|площ|площадь)\.?\s?[\w\s.-]{2,})(?:\d{1,4}[\s.,-]?[\w\s.,-]{2,})?(?:кв|комн|комната|офис|офис|к|квартира)\.?\s?\d{1,4}\b'

    # Ищем контактную информацию в HTML-коде
    contacts = {'phone': [], 'email': [], 'address': []}
    contacts['phone'].extend([match[0] for match in re.findall(phone_regex, html)])
    contacts['email'].extend(re.findall(email_regex, html))
    contacts['address'].extend([match[0] for match in re.findall(address_regex, html)])

    return contacts


def check_figure(soup):
    figures = soup.find_all('figure')
    correct_figures = 0
    errors = []

    for i, figure in enumerate(figures):
        if not figure.find('figcaption'):
            error_msg = f'Отсутствует тег <figcaption> внутри тега <figure>'
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




def check_table(soup, file_path=None):
    tables = soup.find_all('table')
    errors = []
    # encoding = get_encoding(file_path)

    for i, table in enumerate(tables):
        if not table.find('tr') or not (table.find('th') or table.find('td')):
            pattern = re.compile(r'<table(?:\s|>)', re.IGNORECASE)
            error_msg = f'Неправильное использование тега <table> (таблица {i + 1})'
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


def check_nav_tag(soup, file_path=None):
    nav_tags = soup.find_all('nav')
    div_navs = soup.find_all(lambda tag: tag.name == 'div' and ('id' in tag.attrs and tag['id'] == 'nav' or 'class' in tag.attrs and 'nav' in tag['class']))

    if len(nav_tags) > 0 and len(div_navs) == 0:
        return True, []

    errors = []
    if len(div_navs) > 0:
        error_msg = 'Нужно использовать nav вместо div с id/class=nav'
        errors.append(error_msg)

    return False, errors


def correct_errors(soup, errors):
    error_handlers = {
        "Отсутствует тег <figcaption> внутри тега <figure>": handle_figcaption_error,
        "Нужно использовать nav вместо div с id/class=nav": handle_nav_error,
        "Необходимо использовать тег <header> для обозначения шапки страницы": handle_header_error,
        "Необходимо использовать тег <main> для обозначения основного контента страницы": handle_main_error,
        "Необходимо использовать тег <footer> для обозначения подвала страницы": handle_footer_error,
        "Постарайтесь использовать тэг <address> для указания контактной информации автора или владельца сайта": handle_address_error
    }

    corrected_errors = []

    for error in errors:
        if error in error_handlers:
            error_handlers[error](soup)
            corrected_errors.append(error)

    # Удаляем исправленные ошибки из списка errors
    for error in corrected_errors:
        errors.remove(error)

    return soup

def handle_figcaption_error(soup):
    for figure in soup.find_all('figure'):
        if not figure.find('figcaption'):
            figcaption = soup.new_tag('figcaption')
            # Перемещаем всех детей figure в figcaption
            while len(figure.contents) > 0:
                child = figure.contents[0]
                child.extract()
                figcaption.append(child)
            # Добавляем figcaption в figure
            figure.append(figcaption)

def handle_nav_error(soup):
    for div in soup.select('div[id*="nav"], div[class*="nav"], div[id*="navigation"], div[class*="navigation"]'):
        nav = soup.new_tag('nav')
        # Объединяем атрибуты div и nav
        nav.attrs.update(div.attrs)
        # Перемещаем всех детей div в nav
        while len(div.contents) > 0:
            child = div.contents[0]
            child.extract()
            nav.append(child)
        # Заменяем div на nav
        div.replace_with(nav)

def handle_header_error(soup):
    for div in soup.select('div[id*="header"], div[class*="header"], div[id*="head"], div[class*="head"]'):
        header = soup.new_tag('header')
        # Объединяем атрибуты div и header
        header.attrs.update(div.attrs)
        # Перемещаем всех детей div в header
        while len(div.contents) > 0:
            child = div.contents[0]
            child.extract()
            header.append(child)
        # Заменяем div на header
        div.replace_with(header)

def handle_main_error(soup):
    for div in soup.select('div[id*="main"], div[class*="main"], div[id*="content"], div[class*="content"]'):
        main = soup.new_tag('main')
        # Объединяем атрибуты div и main
        main.attrs.update(div.attrs)
        # Перемещаем всех детей div в main
        while len(div.contents) > 0:
            child = div.contents[0]
            child.extract()
            main.append(child)
        # Заменяем div на nav
        div.replace_with(main)

def handle_footer_error(soup):
    for div in soup.select('div[id*="footer"], div[class*="footer"]'):
        footer = soup.new_tag('footer')
        # Объединяем атрибуты div и nav
        footer.attrs.update(div.attrs)
        # Перемещаем всех детей div в nav
        while len(div.contents) > 0:
            child = div.contents[0]
            child.extract()
            footer.append(child)
        # Заменяем div на nav
        div.replace_with(footer)

def handle_address_error(soup):
    # Находим контактную информацию
    contact_info = extract_contact_info(str(soup))

    # Создаем тег <address>
    address = soup.new_tag('address')

    # Добавляем контактную информацию в тег <address>
    for label, texts in contact_info.items():
        for text in texts:
            if text:
                if label == 'phone':
                    phone = soup.new_tag('a', href=f'tel:{text}')
                    phone.string = text
                    address.append(phone)
                elif label == 'email':
                    email = soup.new_tag('a', href=f'mailto:{text}')
                    email.string = text
                    address.append(email)
                elif label == 'address':
                    address_text = soup.new_tag('p')
                    address_text.string = text
                    address.append(address_text)

    # Добавляем тег <address> в конец тега <body>
    body = soup.body
    body.append(address)

    # Удаляем контактную информацию из исходного места
    for label, texts in contact_info.items():
        for text in texts:
            if text:
                if label == 'phone':
                    phone_tag = soup.find('a', href=f'tel:{text}')
                    phone_tag.extract()
                elif label == 'email':
                    email_tag = soup.find('a', href=f'mailto:{text}')
                    email_tag.extract()
                elif label == 'address':
                    address_text = soup.find(string=re.compile(re.escape(text)))
                    address_text.extract()




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


def calculate_score(soup, file_path, criteria):
    total_criteria = len(criteria)
    correct_criteria = [0] * total_criteria
    all_errors = []

    for i, criterion in enumerate(criteria):
        is_correct, errors = criterion(soup, file_path) if isinstance(criterion, types.FunctionType) and 'file_path' in inspect.signature(criterion).parameters else criterion(soup)
        correct_criteria[i] = 1 if is_correct else 0
        all_errors.extend(errors)

    score = sum(correct_criteria) / total_criteria if total_criteria > 0 else 0
    return correct_criteria, all_errors, score

async def process_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

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

    score, errors, ratio = calculate_score(soup, None, criteria)

    corrected_soup = correct_errors(soup, errors)
    corrected_html = corrected_soup.prettify()

    return {'corrected_html': corrected_html, 'errors': errors, 'score': ratio}

