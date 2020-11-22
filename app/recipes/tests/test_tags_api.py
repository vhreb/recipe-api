from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipes.serializers import TagSerializer
from users.tests.test_user_api import UserAPITestMixin


class PublicTagsAPITestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('recipes:tag-list')

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITestCase(UserAPITestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('recipes:tag-list')

    def setUp(self) -> None:
        self.user = self.sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(self.url)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        user2 = self.create_user(
            email='other@gmail.com',
            password='password'
        )
        tag = Tag.objects.create(user=user2, name='Fruity')
        self.client.force_authenticate(user2)
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
