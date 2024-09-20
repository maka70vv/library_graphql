import re

import requests


def get_book_info(isbn):
    url = f'http://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=details&format=json'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        book_key = f'ISBN:{isbn}'
        if book_key in data:
            book_info = data[book_key]['details']
            publish_date = book_info.get('publish_date', '')
            year_match = re.search(r'\d{4}', publish_date)
            publication_year = year_match.group(0) if year_match else None
            return {
                'title': book_info.get('title'),
                'authors': book_info.get('authors', []),
                'publication_year': publication_year,
                'description': book_info.get('description', {}).get('value', ''),
            }
    return None

