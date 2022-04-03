import json
import requests

from bs4 import BeautifulSoup
from functools import reduce
from request_data import headers


def getPageData(url: str, page: int) -> dict:
    """ Получение данных веб-страницы """

    try:
        params = {
            'page': page,
        }

        response = requests.get(url, headers=headers, params=params)
        response.encoding = 'utf-8'
        response.raise_for_status()
    except requests.exceptions.HTTPError as err_http:
        print("Http Error:", err_http)
    except requests.exceptions.ConnectionError as err_conn:
        print("Error Connecting:", err_conn)
    except requests.exceptions.Timeout as err_timeout:
        print("Timeout Error:", err_timeout)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    else:
        print(f"Success request to {page} page")

        return {
            'url': response.url,
            'code': response.status_code,
            'content': response.text
        }

    return {
        'url': url,
        'code': 0,
        'content': ''
    }


def is_json(myjson):
    """ Проверка валидности json """
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


def convertTextToDict(data_str: str):
    if is_json(data_str):
        return json.loads(data_str)
    else:
        return ''


def getBooksData(html: str) -> list:
    books = []

    try:
        soup_object = BeautifulSoup(html, 'lxml')
        class_to_find = {"class": [
            "card card--good card--alternativeMobile js-component"
        ]}

        for book in soup_object.findAll("div", class_to_find):
            book_data = convertTextToDict(book.get("data-ga-product"))

            if not book_data:
                continue

            books.append(book_data)
    except Exception:
        print('An error occurred during data processing')

    return books


def main():
    costs_list = []
    all_books = []

    # > 1
    process_pages = 5

    for page in range(1, process_pages):
        raw_data = getPageData(
            "https://fkniga.ru/catalog/hudozhestvennaja-literatura/",
            page)

        if raw_data['code'] != 200:
            continue

        books_per_page = getBooksData(raw_data['content'])

        # Обработка собранных данных
        costs_list = costs_list + list(map(
            lambda data_dict: data_dict['price'],
            books_per_page))

        all_books = all_books + books_per_page

    books_count = len(costs_list)
    avg_cost = reduce(lambda x, y: x + y, costs_list) / books_count
    print("Средняя стоимость книг: {:.3f}".format(avg_cost))
    print("Количество книг дороже средней стоимости: {:d}".format(
        len([x for x in all_books if x['price'] > avg_cost])))
    print("Всего книг: {:d}".format(books_count))

    # TODO график распределения цен. Средняя цена и точки стоимости книг, выше или ниже этой линии


if __name__ == "__main__":
    main()
