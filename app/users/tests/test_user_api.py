from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


class UserAPITestMixin:

    CREATE_USER_URL = reverse('users:create')
    TOKEN_URL = reverse('users:token')
    ME_URL = reverse('users:me')

    @classmethod
    def create_user(cls, **kwargs):
        return get_user_model().objects.create_user(**kwargs)

    @classmethod
    def sample_user(cls):
        return cls.create_user(email='test@gmail.com', password='testpassword')


class PublicUserApiTestCase(UserAPITestMixin, TestCase):

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
        payload = {
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

    def test_create_token_for_user(self):
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpass',
        }
        self.create_user(**payload)
        res = self.client.post(self.TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        self.create_user(email='test@gmail.com', password='testpass')
        payload = {
            'email': 'test@gmail.com',
            'pass': 'wrong',
        }
        res = self.client.post(self.TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpass',
        }
        res = self.client.post(self.TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        res = self.client.post(self.TOKEN_URL, {'email': 'one', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(self.ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITestCase(UserAPITestMixin, TestCase):

    def setUp(self) -> None:
        self.user = self.create_user(
            email='test@gmail.com',
            password='testpassword',
            name='name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        res = self.client.get(self.ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        res = self.client.post(self.ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        payload = {
            'name': 'newname',
            'password': 'newpassword',
        }
        res = self.client.patch(self.ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
