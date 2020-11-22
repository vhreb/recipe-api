from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


class APITestMixin:

    CREATE_USER_URL = reverse('user:create')

    @classmethod
    def create_user(cls, **kwargs):
        return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTestCase(APITestMixin, TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_valid_user_success(self):
        payload = {
            'email': 'test@gmil.com',
            'password': 'password',
            'name': 'Test name',
        }
        res = self.client.post(self.CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('pass', res.data)

    def test_user_exists(self):
        payload ={
            'email': 'test@gmail.com',
            'password': 'password',
            'name': 'Test name',
        }
        self.create_user(**payload)
        res = self.client.post(self.CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        payload = {
            'email': 'test@gmail.com',
            'password': 'pass',
            'name': 'Test name',
        }
        res = self.client.post(self.CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email'],
        ).exists()
        self.assertFalse(user_exists)
