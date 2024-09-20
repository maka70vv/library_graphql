import json

from graphene_django.utils.testing import GraphQLTestCase

from library_api.schema import schema
from readers.models import Reader


class ReaderTestCase(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    GRAPHQL_URL = "http://localhost:8000/graphql/"

    def test_query_all_readers(self):
        Reader.objects.create(name="Reader 1", email="reader1@example.com")
        Reader.objects.create(name="Reader 2", email="reader2@example.com")

        query = '''
        query {
            allReaders {
                name
                email
            }
        }
        '''
        response = self.query(query)

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)
        self.assertEqual(len(content['data']['allReaders']), 2)
        self.assertEqual(content['data']['allReaders'][0]['name'], 'Reader 1')
        self.assertEqual(content['data']['allReaders'][0]['email'], 'reader1@example.com')

    def test_create_reader(self):
        mutation = '''
        mutation createReader($name: String!, $email: String!) {
            createReader(name: $name, email: $email) {
                reader {
                    name
                    email
                }
            }
        }
        '''
        variables = {
            'name': 'New Reader',
            'email': 'newreader@example.com'
        }
        response = self.query(
            mutation,
            variables=variables
        )

        self.assertResponseNoErrors(response)

        content = json.loads(response.content)
        self.assertIn('createReader', content['data'])
        self.assertEqual(content['data']['createReader']['reader']['name'], 'New Reader')
        self.assertEqual(content['data']['createReader']['reader']['email'], 'newreader@example.com')

        reader_exists = Reader.objects.filter(email='newreader@example.com').exists()
        self.assertTrue(reader_exists)
