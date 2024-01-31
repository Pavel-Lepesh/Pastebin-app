from django.test import TestCase
from .models import Note
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from copy import deepcopy


class NoteTests(TestCase):
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
