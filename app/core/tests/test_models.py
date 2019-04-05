from django.test import TestCase

from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_succefully(self):
        """ Testing if a new user is created with email """
        email = 'test@test.com'
        password = 'test@123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalised(self):
        """ Test the email for a new user is normalised """
        email = 'test@TEST.COM'
        user = get_user_model().objects.create_user(email, 'test@123')
        self.assertEqual(user.email, email.lower())

    def test_create_new_super_user(self):
        """ Testing if we are able to create superuser """
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'test@123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
