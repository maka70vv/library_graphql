import requests


def get_book_info(isbn):
    url = f'http://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=details&format=json'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        book_key = f'ISBN:{isbn}'
        if book_key in data:
            book_info = data[book_key]['details']
            return {
                'title': book_info.get('title'),
                'authors': book_info.get('authors', []),
                'publication_year': book_info.get('publish_date', '').split('-')[0],
                'description': book_info.get('description', {}).get('value', ''),
            }
    return None

