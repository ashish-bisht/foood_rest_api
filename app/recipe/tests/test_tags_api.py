from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag

from recipe.serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """ Testing tags if no authentication provided """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ test that login is required for retrieving tags """
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, 401)


class PrivateTagsApiTests(TestCase):
    """ Test Authorised user tags API """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com', 'test@123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """ Retreving all tags which are created  """
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name="Non Vegeterian")

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ Test taht tags returned are for authenticated current user """
        user2 = get_user_model().objects.create_user(
            'other@other.com', 'test@123'
        )
        Tag.objects.create(user=user2, name='Pizza')
        tag = Tag.objects.create(user=self.user, name='Burger')

        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """ Testing , posting a new tag"""
        payload = {'name': 'Tag Test'}
        self.client.post(TAG_URL, payload)

        exists = Tag.objects.filter(
            user=self.user, name=payload['name']).exists()
        self.assertTrue(exists)

    def test_create_invalid_tag(self):
        """ Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAG_URL, payload)
        self.assertEqual(res.status_code, 400)
