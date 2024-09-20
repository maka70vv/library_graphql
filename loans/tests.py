import json
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token

from books.models import Book, Author
from library_api.schema import schema
from readers.models import Reader
from loans.models import Loan


class LoanTestCase(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    GRAPHQL_URL = "http://localhost:8000/graphql/"

    def setUp(self):
        super().setUp()
        self.author = Author.objects.create(name='Author Name', biography='Author Biography')
        self.book = Book.objects.create(title='Book Title', publication_year=2023, isbn='1234567890')
        self.book.authors.add(self.author)
        self.user = self._create_test_user()

    def _create_test_user(self):
        user_model = get_user_model()
        return user_model.objects.create_superuser(
            email='testuser@example.com',
            password='testpass',
            first_name='Test',
            last_name='User'
        )

    def test_create_loan(self):
        user = get_user_model().objects.get(pk=1)
        token = get_token(user)
        headers = {"AUTHORIZATION": f"JWT {token}"}

        mutation = '''
        mutation createLoan($bookId: ID!, $loanEndDate: Date!) {
            createLoan(bookId: $bookId, loanEndDate: $loanEndDate) {
                loan {
                    book {
                        title
                    }
                    reader {
                        email
                    }
                    loanEndDate
                }
            }
        }
        '''
        loan_end_date = (datetime.now() + timedelta(days=14)).date().isoformat()
        variables = {
            'bookId': self.book.id,
            'loanEndDate': loan_end_date
        }
        response = self.query(
            mutation,
            variables=variables,
            headers=headers
        )

        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertIn('createLoan', content['data'])
        self.assertEqual(content['data']['createLoan']['loan']['book']['title'], 'Book Title')
        self.assertEqual(content['data']['createLoan']['loan']['reader']['email'], 'testuser@example.com')

    def test_return_book(self):
        user = get_user_model().objects.get(pk=1)
        token = get_token(user)
        headers = {"AUTHORIZATION": f"JWT {token}"}

        reader = Reader.objects.create(email=self.user.email, name=f"{self.user.first_name} {self.user.last_name}")
        loan = Loan.objects.create(
            book=self.book,
            reader=reader,
            loan_date=datetime.now().date(),
            loan_end_date=(datetime.now() + timedelta(days=14)).date()
        )

        mutation = '''
        mutation returnBook($loanId: ID!) {
            returnBook(loanId: $loanId) {
                success
            }
        }
        '''
        variables = {
            'loanId': str(loan.id),
        }
        response = self.query(
            mutation,
            variables=variables,
            headers=headers
        )

        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertTrue(content['data']['returnBook']['success'])

        loan.refresh_from_db()
        self.assertTrue(loan.is_returned)
        self.assertIsNotNone(loan.return_date)
