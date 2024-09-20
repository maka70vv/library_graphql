import json
from django.contrib.auth import get_user_model
from graphene_django.utils import GraphQLTestCase
from graphql_jwt.shortcuts import get_token

from library_api.schema import schema


class ApiTestCase(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

    def setUp(self):
        super().setUp()
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            email='testuser@example.com',
            password='testpass',
            first_name='Test',
            last_name='User'
        )

    def test_create_user(self):
        mutation = '''
        mutation {
            createUser(email: "newuser@example.com", password: "newpass", firstName: "New", lastName: "User") {
                user {
                    email
                    firstName
                    lastName
                }
            }
        }
        '''
        response = self.query(
            mutation,
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertIn('data', content)
        self.assertIn('createUser', content['data'])
        self.assertEqual(content['data']['createUser']['user']['email'], 'newuser@example.com')

    def test_token_auth(self):
        mutation = '''
        mutation {
            tokenAuth(email: "testuser@example.com", password: "testpass") {
                token
            }
        }
        '''
        response = self.query(
            mutation,
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertIn('data', content)
        self.assertIn('tokenAuth', content['data'])
        self.assertIn('token', content['data']['tokenAuth'])

    def test_me_query(self):
        token = get_token(self.user)
        headers = {"HTTP_AUTHORIZATION": f"JWT {token}"}
        query = '''
        {
            me {
                email
                firstName
                lastName
            }
        }
        '''
        response = self.query(
            query,
            headers=headers
        )
        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        self.assertIn('data', content)
        self.assertIn('me', content['data'])
        self.assertEqual(content['data']['me']['email'], self.user.email)
        self.assertEqual(content['data']['me']['firstName'], self.user.first_name)
        self.assertEqual(content['data']['me']['lastName'], self.user.last_name)
