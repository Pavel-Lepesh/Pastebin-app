from django.test import TestCase
from .models import Note
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.urls import reverse
from copy import deepcopy
from hash_generator.generator import generator
from .s3_storage import s3_storage


class NoteModelTests(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username='Test User',
                                                  password='1234')
        self.data = {
            'title': 'Test note',
            'hash_link': 123456789,
            'expiration': None,
            'user': self.test_user,
            'key_for_s3': '123e4567-e89b-12d3-a456-426655440000',
            'availability': 'public'
        }
        self.test_note = Note.objects.create(**self.data)

    def tearDown(self):
        def delete_note():
            self.test_note.delete()

        def delete_user():
            self.test_user.delete()

        transaction.on_commit(delete_note)
        transaction.on_commit(delete_user)

    def test_create_note(self):
        self.assertIsInstance(self.test_note, Note)

    def test_invalid_key_for_s3(self):
        data = deepcopy(self.data)
        data['key_for_s3'] = '1234'
        with self.assertRaises(ValidationError):
            Note.objects.create(**data)

    def test_invalid_availability(self):
        data = deepcopy(self.data)
        data['availability'] = 'invalid_value'
        with self.assertRaises(ValidationError):
            Note.objects.create(**data)


class JWTTests(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username='Test User',
                                                  password='1234')

    def tearDown(self):
        def delete_user():
            self.test_user.delete()

        transaction.on_commit(delete_user)

    def test_return_tokens(self):
        response = self.client.post(reverse('token_obtain_pair'),
                                    data={"username": "Test User",
                                          "password": "1234"},
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_trough_refresh(self):
        response = self.client.post(reverse('token_obtain_pair'),
                                    data={"username": "Test User",
                                          "password": "1234"},
                                    content_type="application/json")
        refresh_token = response.data.get("refresh")
        result_response = self.client.post(reverse("token_refresh"),
                                           data={"refresh": refresh_token},
                                           content_type="application/json")
        self.assertEqual(result_response.status_code, 200)
        self.assertIn('access', result_response.data)


class NoteActionsTests(TestCase):
    def setUp(self):
        self.test_data = {
                          "title": "string",
                          "content": "string",
                          "user": 0,
                          "expiration": 0,
                          "key_for_s3": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                          "availability": "string"
                        }
        self.test_user = User.objects.create_user(username='Test User',
                                                  password='1234')
        response = self.client.post(reverse('token_obtain_pair'),
                                    data={"username": "Test User",
                                          "password": "1234"},
                                    content_type="application/json")
        self.access_token = response.data.get("access")
        generator.start_generate()

    def tearDown(self):
        def delete_user():
            self.test_user.delete()

        transaction.on_commit(delete_user)

    def test_create_note(self):
        try:
            response = self.client.post(reverse("get_create_note"),
                                        data={
                                            "title": "string",
                                            "content": "string",
                                            "availability": "public",
                                            "expiration": 100
                                        },
                                        headers={
                                            "Authorization": f"Bearer {self.access_token}"
                                        },
                                        content_type="application/json")
        except Exception as error:
            self.assertFalse(True, msg=error)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.keys(), self.test_data.keys())

        s3_storage.delete_object(str(response.data.get("key_for_s3")))
