from django.test import TestCase

from .models import User


class SimpleAccountsTests(TestCase):
    def test_create_and_delete_user(self):
        user_data = {
            'username': 'Test',
            'password': '1234',
            'email': 'test@gmail.com'
        }

        User.objects.create_user(**user_data)
        self.assertEqual(User.objects.all().count(), 1)

        user = User.objects.get(email=user_data['email'])
        self.assertTrue(User.objects.all().contains(user))

        User.objects.filter(email=user_data['email']).delete()
        self.assertEqual(User.objects.all().count(), 0)
