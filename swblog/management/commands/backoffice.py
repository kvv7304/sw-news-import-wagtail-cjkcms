import datetime
import json
import pprint
import re
import sys
import traceback
from io import BytesIO

from anticaptchaofficial.imagecaptcha import *
from bs4 import BeautifulSoup

import swblog.management.commands.config as config


class myDict(dict):
    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        else:
            return None

def bypass_captcha(session, captcha_key = config.captcha_key):
    solver = imagecaptcha()
    # solver.set_verbose(0)  # Установите уровень отладки на 0, чтобы отключить сообщения работы

    while True:
        try:
            solver.set_key(captcha_key)
            img = session.get("https://ru.siberianhealth.com/ru/captcha/default/")
            captcha_content = BytesIO(img.content)
            captcha_text = solver.solve_and_return_solution(file_path=None, body=captcha_content.read())
            return captcha_text
        except:
            pass

def auth(user, url="https://ru.siberianhealth.com/ru/backoffice-new/?newStyle=yes", url_ajax = "https://ru.siberianhealth.com/ru/controller/ajax/"):

    payload = {
        "login": f"{user.number}",
        "pass": f"{user.password}",
        "url": url,
        "_controller": "Backoffice_Auth/submit",
        "_url": "https://ru.siberianhealth.com/ru/backoffice/auth/?url=https://ru.siberianhealth.com/ru/backoffice-new/?newStyle=yes"
    }

    with requests.Session() as session:
        while True :
            response = session.post(url=url_ajax, data=payload, allow_redirects=True)
            response_json = response.json()
            if response_json['result']['status'] == "Denied":
                payload["captcha"] = bypass_captcha(session)
            else:
                break
        if response_json['result']['success'] and "Стать Бизнес-Партнером" not in session.get(url=url).text:
            return session
        elif "Стать Бизнес-Партнером" in session.get(url=url).text:
            return f"{user.number} нужно стать Бизнес-Партнером"
        else:
            return f"{user.number} {response_json['result']['status']}"


def get_current_period(format):
    return datetime.now().strftime(format)

def get_data(session, url):
    while True:
        try:
            response = session.get(url)
            # response.raise_for_status()
            html_content = response.text
            return html_content
        except ValueError as e:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))} Произошла ошибка при чтении таблиц из HTML: {e} {url}")
            time.sleep(60)
        except AttributeError:
            # Обработка ошибки
            return None
        except Exception as e:
            print("Произошла ошибка:", e)
            traceback.print_exc()
            time.sleep(60)

def process_user_data(user, url):
    session = None

    try:
        session = auth(user)
        if isinstance(session, requests.sessions.Session):
            news = get_data(session, url)
            # Выход из цикла, если все прошло успешно
            return news
        else:
            return session
    except Exception as e:
        print("Произошла ошибка:", e)
        traceback.print_exc()
        time.sleep(60)
    finally:
        # Закрываем сессию, если она была создана и является объектом Session
        if session and isinstance(session, requests.sessions.Session):
            session.close()


def parse_russian_date(date_string):
    # Словарь для сопоставления русских названий месяцев с английскими
    months = {
        'января': 'January',
        'февраля': 'February',
        'марта': 'March',
        'апреля': 'April',
        'мая': 'May',
        'июня': 'June',
        'июля': 'July',
        'августа': 'August',
        'сентября': 'September',
        'октября': 'October',
        'ноября': 'November',
        'декабря': 'December'
    }

    try:
        # Замена русского месяца в строке даты на английский эквивалент
        for rus, eng in months.items():
            date_string = date_string.replace(rus, eng)
        # Разбор даты, предполагая формат день месяц год (месяц на английском)
        parsed_date = datetime.strptime(date_string, '%d %B %Y')
        return parsed_date.strftime('%Y-%m-%d')
    except ValueError as e:
        print(f'Ошибка: {e}')
        return None


def clean_html_content(soup):
    # Список тегов, которые мы хотим сохранить.
    allowed_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'a', 'li', 'ul', 'ol', 'blockquote', 'pre', 'div',
                    'video', 'audio', 'canvas', 'table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot', 'form', 'input',
                    'textarea', 'button', 'select', 'option', 'details', 'summary', 'dialog', 'section', 'article',
                    'aside', 'header', 'footer', 'nav', 'b', 'i', 'u', 'em', 'strong', 'small', 'mark', 'del', 'ins',
                    'sub', 'sup', 'code', 'kbd', 'samp', 'var', 'dd', 'dl', 'dt', 'figcaption', 'figure', 'abbr', 'q',
                    'cite', 'dfn', 'time' ]

    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.decompose()
            continue

        if tag.name == 'p' and "Скачать эту новость" in tag.text.strip():
            tag.decompose()
            continue

        if tag.get('style'):
            tag['style'] = ""

        if tag.name == "a":
            href_value = tag.get('href')

            if href_value and href_value.startswith('/ru/'):
                new_href = 'https://ru.siberianhealth.com' + href_value + '?referral=2596572021'
                tag['href'] = new_href

            if href_value and 'ru.siberianhealth.com' in href_value and '?' not in href_value:
                new_href = href_value + '?referral=2596572021'
                tag['href'] = new_href

            if href_value and 'ru.siberianhealth.com' not in href_value:
                tag['target'] = '_blank'

    return str(soup).strip()


def yandex_translit(text):
    """
    Преобразует заданный текст в slug, используя правила транслитерации Яндекса.

    :param text: str - Текст, подлежащий транслитерации и дополнению
    :return: str - Получившийся slug
    """
    # Применение правил транслитерации Яндекса с использованием translitcodec
    # (смоделированных здесь с использованием базового отображения)
    # Обычно мы бы использовали translitcodec, но в этой среде он недоступен.
    # Отображение основано на распространенной транслитерации (не специфичной для какой-либо библиотеки).
    # Текущая логика функции
    translit_table = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
        'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
        'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
        'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
        'я': 'ya'
    }
    translit_text = ''.join(translit_table.get(char, char) for char in text.lower())
    slug = re.sub(r'\s+|[^a-zA-Z0-9-]', '-', translit_text)
    slug = re.sub('-+', '-', slug)
    slug = slug.strip('-')
    return slug


def extract_news_data(div):
    if div.find('span', class_='bo--page-news-preview__tag'):
        caption_tag = div.find('span', class_='bo--page-news-preview__tag').text
    else:
        caption_tag = "News"

    title = str(div.find('h4').text).strip()
    slug = yandex_translit(str(title))
    body_url = div.find('a', class_='bo--page-news-preview__link')['data-share-url']
    image_url = div.find('img', class_='bo--page-news-preview__image')['src']
    date_display = parse_russian_date(div.find('time', class_='bo--page-news-preview__date').text)

    description = (
        f"Узнайте все о {title} с компанией Сибирское здоровье (Siberian Wellness). "
        f"Ключевые темы: {caption_tag}. "
        f"Присоединяйтесь к нашему сообществу и откройте для себя все возможности продукции и бизнеса. "
        f"Читайте последние новости и обновления о {title}. "
        f"Узнайте больше на сайте Знайкиной Марины и начните ваш путь к успеху с Сибирское здоровье (Siberian Wellness)."
    )
    return {
        "title": title,
        "slug": slug,
        "body_url": body_url,
        "caption_tag": caption_tag,
        "image_url": image_url,
        "date_display": date_display,
        "description": description,
    }


def parser_backoffice_page_news_list(user_data):
    soup = BeautifulSoup(user_data, 'html.parser')
    parent_div = soup.find('div', class_='bo--page-news-grid')
    user_data = []
    if parent_div:
        divs_to_find = parent_div.find_all('div', class_='bo--page-news-preview')
        for div in divs_to_find:
            news_data = extract_news_data(div)
            user_data.append(news_data)
    return user_data


def backoffice_page_news_list(user=config.user):
    try:
        user_data = process_user_data(myDict(user), "https://ru.siberianhealth.com/ru/backoffice/news/")
        page_news_grid = parser_backoffice_page_news_list(user_data)
        return page_news_grid

    except Exception as e:
        # Блок обработки исключений
        print("Произошла ошибка:", e)
        traceback.print_exc()
        time.sleep(60)



def parser_backoffice_page_news(user_data):
    soup = BeautifulSoup(user_data, 'html.parser')
    parent_div = soup.find('div', class_='bo--page-news-single__content')
    page_news = clean_html_content(parent_div)
    return page_news.strip()

def parser_backoffice_page_news_old(user_data):
    soup = BeautifulSoup(user_data, 'html.parser')
    parent_div = soup.find('div', class_='news-page')
    page_news = clean_html_content(parent_div)
    return page_news



def backoffice_page_news(url, user = config.user):
    try:
        user_data = process_user_data(myDict(user),url)
        page_news = parser_backoffice_page_news(user_data)
        page_news += f'<p><a href="{url}">' \
                     f'Новость взята с официального сайта Компании «Сибирское здоровье» Siberian Wellness.</a></p>'

        return page_news.strip()


    except Exception as e:
        # Блок обработки исключений
        print("Произошла ошибка:", e)
        traceback.print_exc()
        time.sleep(60)


def backoffice_page_news_old(url, user = config.user):
    try:
        user_data = process_user_data(myDict(user),url)
        page_news = parser_backoffice_page_news_old(user_data)
        page_news += f'<p><a href="{url}">' \
                     f'Новость взята с официального сайта Компании «Сибирское здоровье» Siberian Wellness.</a></p>'

        return page_news

    except Exception as e:
        # Блок обработки исключений
        print("Произошла ошибка:", e)
        traceback.print_exc()
        time.sleep(60)



def parser_backoffice_page_news_data(user_data):
    soup = BeautifulSoup(user_data, 'html.parser')
    # print(soup.prettify().encode(sys.stdout.encoding, errors='replace').decode('cp1251'))
    news_items = soup.find_all('div', class_='g_15 alpha')
    year_tag = soup.find('div', style='margin: 0 0 10px 40px;display: inline-block;min-width:105px')
    if year_tag:
        year = year_tag.text.strip().split('→')[-1].strip().split(' ')[-1]
    else:
        year = ""

    user_data = []
    for news_item in news_items:
        title_tag = news_item.find('h2', class_='f180').find('a')
        title = title_tag.text.strip()
        slug = yandex_translit(str(title))
        body_url = f"https://ru.siberianhealth.com{title_tag['href']}"
        caption_tag = "News"

        previous_sibling_text = news_item.find_previous_sibling('div').text.strip()
        date_string = previous_sibling_text[:2] + " " + previous_sibling_text[2:].lower() + " " + year
        date_display = parse_russian_date(date_string)
        user_data.append({
            "title": title,
            "slug": slug,
            "body_url": body_url,
            "caption_tag": caption_tag,
            "image_url": None,
            "date_display": date_display
        })
    return user_data


def backoffice_page_news_all(user=config.user):
    # url = f"https://ru.siberianhealth.com/ru/news/list/internal/{datetime.now().strftime('%m-%Y')}/1/"
    url = f"https://ru.siberianhealth.com/ru/news/list/internal/01-2024/1/"
    page_news_grid = []
    try:
        user_data = process_user_data(myDict(user), url)
        if user_data:  # Проверяем, что user_data не пустой
            page_news_grid.extend(parser_backoffice_page_news_data(user_data))
    except Exception as e:
        print("Произошла ошибка:", e)
        traceback.print_exc()
        time.sleep(60)
    return page_news_grid


def get_report(session, url, year, month):
    data = {
        'year': year,
        'month': month,
        '_controller': 'Backoffice_News/load',
        '_contract': '2596572021',
        '_url' : 'https://ru.siberianhealth.com/ru/backoffice/news/'
  }
    try:
        response = session.post("https://ru.siberianhealth.com/ru/backoffice/news/", data=data)
        response.raise_for_status()
        html_content = response.text
        return html_content

    except Exception as e:
        print("Произошла ошибка:", e)
        traceback.print_exc()


def get_news_old(session, url, data):

    try:
        response = session.post(url, data=data)
        response.raise_for_status()
        html_content = response.text
        return html_content

    except Exception as e:
        print("Произошла ошибка:", e)
        traceback.print_exc()


def getting_old_news(year: str, month: str):
    data = {
        'year': year,
        'month': month,
        '_controller': 'Backoffice_News/load',
        '_contract': '2596572021',
        '_url': 'https://ru.siberianhealth.com/ru/backoffice/news/',
    }
    user_data = []
    try:
        # Аутентификация и получение сессии
        session = auth(myDict(config.user), url="https://ru.siberianhealth.com/ru/backoffice/news/")
        if isinstance(session, requests.sessions.Session):
            # Получение старых новостей
            news_old_json = get_news_old(session, 'https://ru.siberianhealth.com/ru/controller/ajax/', data=data)
            if news_old_json:
                # Обработка и парсинг JSON данных
                news_old = json.loads(news_old_json)
                news_soup = BeautifulSoup(news_old['result']['html'], 'html.parser')
                # Извлечение данных новостей
                for div in news_soup.find_all('div', class_='bo--page-news-preview'):
                    news_data = extract_news_data(div)
                    user_data.append(news_data)

        return user_data

    except Exception as e:
        print("Произошла ошибка:", e)
        traceback.print_exc()
        time.sleep(60)
        return None

    finally:
        # Закрытие сессии, если она была создана
        if session and isinstance(session, requests.sessions.Session):
            session.close()

if __name__ == '__main__':
    print(getting_old_news(2024, 1))
