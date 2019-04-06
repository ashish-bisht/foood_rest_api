from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """ Test the users API  """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """ To test if user is created with proper payload """
        payload = {
            'email': 'test@test.com',
            'password': 'testpass',
            'name': 'Test Test'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, 201)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """ Test to check if user already exists  """
        payload = {
            'email': 'test@test.com',
            'password': 'testpass',
            'name': 'Test Test'
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, 400)

    def test_password_too_short(self):
        """ Test if password is too small """
        payload = {
            'email': 'test@test.com',
            'password': 'test',
            'name': 'Test Test'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, 400)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ Test that token is created for the user """

        payload = {
            'email': 'test@test.com',
            'password': 'test@test.com',
            'name': 'Test Test'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, 200)

    def test_create_token_invalid_credentials(self):
        """ Test if token is not created when wrong credentials are passed """
        create_user(email='test@test.com', password='test@test.com')
        payload = {
            'email': 'test@test.com',
            'password': 'test@123',
            'name': 'Test Test'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, 400)

    def test_create_token_no_user_created(self):
        """ Test if no token is created if user is not created  """
        payload = {
            'email': 'test@test.com',
            'password': 'test@123',
            'name': 'Test Test'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, 400)

    def test_create_token_missing_field(self):
        """ Test taht email and password are required """
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, 400)
