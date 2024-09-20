import json

from django.contrib.auth import get_user_model
from graphene_django.utils import GraphQLTestCase
from graphql_jwt.shortcuts import get_token

from library_api.schema import schema
from .models import Author, Book


class ApiTestCase(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    GRAPHQL_URL = "http://localhost:8000/graphql/"

    def setUp(self):
        super().setUp()
        user_model = get_user_model()
        self.user = user_model.objects.create_superuser(email='testuser', password='testpass', first_name='testuser',
                                                        last_name='testuser')
        self.author = Author.objects.create(name='Author Name', biography='Author Biography')
        self.book = Book.objects.create(title='Book Title', publication_year=2023, isbn='1234567890')
        self.book.authors.add(self.author)

    def test_query_all_books(self):
        query_data = '''
        {
            allBooks {
                books {
                    title
                    publicationYear
                }
                totalCount
            }
        }
        '''
        response = self.query(
            query_data,
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertIn('data', content)
        self.assertIn('allBooks', content['data'])
        self.assertEqual(content['data']['allBooks']['totalCount'], 1)
        self.assertEqual(content['data']['allBooks']['books'][0]['title'], 'Book Title')

    def test_create_author_mutation(self):
        user = get_user_model().objects.get(pk=1)
        token = get_token(user)
        headers = {"AUTHORIZATION": f"JWT {token}"}
        mutation = '''
        mutation {
            createAuthor(name: "New Author", biography: "New Biography") {
                author {
                    name
                }
            }
        }
        '''
        response = self.query(
            mutation,
            headers=headers,
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertIn('data', content)
        self.assertIn('createAuthor', content['data'])
        self.assertEqual(content['data']['createAuthor']['author']['name'], 'New Author')

    def test_create_rating_mutation(self):
        user = get_user_model().objects.get(pk=1)
        token = get_token(user)
        headers = {"AUTHORIZATION": f"JWT {token}"}
        mutation = '''
        mutation {
            createRating(bookId: %d, score: 5) {
                rating {
                    score
                }
            }
        }
        ''' % self.book.id
        response = self.query(
            mutation,
            headers=headers,
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertIn('data', content)
        self.assertIn('createRating', content['data'])
        self.assertEqual(content['data']['createRating']['rating']['score'], 5)

    def test_search_books_by_name(self):
        query = '''
        {
            searchBooks(title: "Book Title") {
                title
            }
        }
        '''
        response = self.query(
            query,
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertIn('data', content)
        self.assertIn('searchBooks', content['data'])
        self.assertEqual(len(content['data']['searchBooks']), 1)
        self.assertEqual(content['data']['searchBooks'][0]['title'], 'Book Title')

    def test_search_books_by_author_name(self):
        query = '''
        {
            searchBooks(authorName: "Author Name") {
                title
            }
        }
        '''
        response = self.query(
            query,
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertIn('data', content)
        self.assertIn('searchBooks', content['data'])
        self.assertEqual(len(content['data']['searchBooks']), 1)
        self.assertEqual(content['data']['searchBooks'][0]['title'], 'Book Title')

    def test_search_books_by_dates(self):
        query = '''
        {
            searchBooks(yearGte: 2023, yearLte: 2025) {
                title
            }
        }
        '''
        response = self.query(
            query,
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertIn('data', content)
        self.assertIn('searchBooks', content['data'])
        self.assertEqual(len(content['data']['searchBooks']), 1)
        self.assertEqual(content['data']['searchBooks'][0]['title'], 'Book Title')

    def test_create_book_by_isbn_mutation(self):
        user = get_user_model().objects.get(pk=1)
        token = get_token(user)
        headers = {"AUTHORIZATION": f"JWT {token}"}
        mutation = '''
        mutation {
            createBookByIsbn(isbn: "1234567890") {
                book {
                    title
                    isbn
                }
            }
        }
        '''
        response = self.query(
            mutation,
            headers=headers,
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertIn('data', content)
        self.assertIn('createBookByIsbn', content['data'])
        self.assertEqual(content['data']['createBookByISBN']['book']['isbn'], '1234567890')
