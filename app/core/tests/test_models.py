from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models
from users.tests.test_user_api import UserAPITestMixin


class ModelTests(UserAPITestMixin, TestCase):

    def setUp(self) -> None:
        self.password = 'Testpass123'

    def test_create_user_with_email_successful(self):
        email = 'test@gmail.com'
        user = get_user_model().objects.create_user(
            email=email,
            password=self.password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(self.password))

    def test_new_user_email_normalized(self):
        email = 'test@GMAIL.COM'
        user = get_user_model().objects.create_user(email, self.password)

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        invalid_emails = (
            None,
            12345,
            23.123,
            '',
        )
        for email in invalid_emails:
            with self.assertRaises(ValueError):
                get_user_model().objects.create_user(email, self.password)

    def test_create_new_superuser(self):
        user = get_user_model().objects.create_superuser(
            'test@gmail.com',
            self.password
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        tag = models.Tag.objects.create(
            user=self.sample_user(),
            name='Vegan',
        )

        self.assertEqual(str(tag), tag.name)
