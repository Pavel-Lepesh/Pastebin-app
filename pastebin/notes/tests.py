import django

django.setup()
import json
from copy import copy, deepcopy

from accounts.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import Client, TestCase
from django.urls import reverse
from hash_generator.generator import generator
from rest_framework.test import APITestCase
from s3_storage import s3_storage

from .models import Note


class NoteModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_user = User.objects.create_user(username='Test User',
                                                 password='1234')
        cls.data = {
            'title': 'Test note',
            'hash_link': 123456789,
            'expiration': None,
            'user': cls.test_user,
            'key_for_s3': '123e4567-e89b-12d3-a456-426655440000',
            'availability': 'public'
        }
        cls.test_note = Note.objects.create(**cls.data)

    @classmethod
    def tearDownClass(cls):
        def delete_note():
            cls.test_note.delete()

        def delete_user():
            cls.test_user.delete()

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
        self.test_user = User.objects.create_user(username='Test User2',
                                                  password='1234')

    def tearDown(self):
        def delete_user():
            self.test_user.delete()

        transaction.on_commit(delete_user)

    def test_return_tokens(self):
        response = self.client.post(reverse('token_obtain_pair'),
                                    data={"username": "Test User2",
                                          "password": "1234"},
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_trough_refresh(self):
        response = self.client.post(reverse('token_obtain_pair'),
                                    data={"username": "Test User2",
                                          "password": "1234"},
                                    content_type="application/json")
        refresh_token = response.data.get("refresh")
        result_response = self.client.post(reverse("token_refresh"),
                                           data={"refresh": refresh_token},
                                           content_type="application/json")
        self.assertEqual(result_response.status_code, 200)
        self.assertIn('access', result_response.data)


class GetCreateNotesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result_post = {
            'title',
            'content',
            'user',
            'expiration',
            'key_for_s3',
            'availability',
            'hash_link'
        }
        cls.result_get = {
            'title',
            'hash_link',
            'time_create',
            'user'
        }
        cls.test_user = User.objects.create_user(username='Test User3',
                                                 password='1234',
                                                 email='1234@gmail.com')
        client = Client()
        response = client.post(reverse('token_obtain_pair'),
                               data={"username": "Test User3",
                                     "password": "1234"},
                               content_type="application/json",
                               )

        assert response.status_code == 200

        cls.token = response.data['access']

        assert isinstance(cls.token, str)

        generator.start_generate()

    @classmethod
    def tearDownClass(cls):
        def delete_user():
            cls.test_user.delete()

        transaction.on_commit(delete_user)

    def check_connection_s3(self):
        result = s3_storage.check_connection()
        self.assertTrue(result)

    def test_create_and_get_note(self):
        data = {
            'title': 'string',
            'content': 'string',
            'availability': 'public',
            'expiration': 120
        }
        post_response = self.client.post(reverse('get_create_note'),
                                         data=data,
                                         headers={
                                             'Authorization': f'Bearer {self.token}'
                                         },
                                         content_type="application/json",
                                         )
        self.assertEqual(post_response.status_code, 201)
        self.assertEqual(self.result_post, post_response.data.keys())

        get_response = self.client.get(reverse('get_create_note'),
                                       headers={
                                           'Authorization': f'Bearer {self.token}'
                                       }
                                       )
        s3_storage.delete_object(str(post_response.data['key_for_s3']))

        self.assertIsInstance(get_response.data, list)
        self.assertEqual(1, len(get_response.data))
        self.assertEqual(self.result_get, get_response.data[0].keys())

    def test_get_public_notes(self):
        data = {
            'title': 'string',
            'content': 'string',
            'availability': 'public',
            'expiration': 120
        }
        post_response1 = self.client.post(reverse('get_create_note'),
                                          data=data,
                                          headers={
                                              'Authorization': f'Bearer {self.token}'
                                          },
                                          content_type="application/json",
                                          )
        self.assertEqual(post_response1.status_code, 201)

        data['availability'] = 'private'
        post_response2 = self.client.post(reverse('get_create_note'),
                                          data=data,
                                          headers={
                                              'Authorization': f'Bearer {self.token}'
                                          },
                                          content_type="application/json",
                                          )
        self.assertEqual(post_response2.status_code, 201)
        get_response = self.client.get(f'/api/v1/notes/usernotes/{self.test_user.id}')

        s3_storage.delete_object(str(post_response1.data['key_for_s3']))
        s3_storage.delete_object(str(post_response2.data['key_for_s3']))

        self.assertEqual(get_response.status_code, 200)
        self.assertIsInstance(get_response.data, list)
        self.assertEqual(len(get_response.data), 1)


class BaseAccess(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = {
            'title': 'string',
            'content': 'string',
            'availability': 'public',
            'expiration': 120
        }
        cls.test_user = User.objects.create_user(username='Test User4',
                                                 password='1234',
                                                 email='1234@gmail.com')
        client = Client()
        user_response = client.post(reverse('token_obtain_pair'),
                                    data={"username": "Test User4",
                                          "password": "1234"},
                                    content_type="application/json",
                                    )
        cls.token = user_response.data['access']
        cls.post_response = client.post(reverse('get_create_note'),
                                        data=cls.data,
                                        headers={
                                            'Authorization': f'Bearer {cls.token}'
                                        },
                                        content_type="application/json",
                                        )
        cls.hash_link = cls.post_response.data['hash_link']
        generator.start_generate()

    @classmethod
    def tearDownClass(cls):
        def delete_user():
            cls.test_user.delete()

        transaction.on_commit(delete_user)
        s3_storage.delete_object(str(cls.post_response.data['key_for_s3']))

    def test_get_note(self):
        get_response = self.client.get(reverse('note-detail', kwargs={'hash_link': self.hash_link}))

        self.assertEqual(200, get_response.status_code)
        self.assertEqual(self.data['content'], get_response.data['content'])

    def test_update_note(self):
        update_data = copy(self.data)
        update_data['content'] = 'update content'
        update_response = self.client.put(reverse('note-detail', kwargs={'hash_link': self.hash_link}),
                                          data=json.dumps(update_data),
                                          headers={
                                              'Authorization': f'Bearer {self.token}'
                                          },
                                          content_type="application/json")

        self.assertEqual(201, update_response.status_code)
        get_response = self.client.get(reverse('note-detail', kwargs={'hash_link': self.hash_link}))

        self.assertEqual('update content', get_response.data['content'])

    def test_patch_note(self):
        patch_data = copy(self.data)
        patch_data['content'] = 'patch content'
        patch_response = self.client.put(reverse('note-detail', kwargs={'hash_link': self.hash_link}),
                                         data=json.dumps(patch_data),
                                         headers={
                                             'Authorization': f'Bearer {self.token}'
                                         },
                                         content_type="application/json")
        self.assertEqual(201, patch_response.status_code)

        get_response = self.client.get(reverse('note-detail', kwargs={'hash_link': self.hash_link}))

        self.assertEqual('patch content', get_response.data['content'])

    def test_delete_note(self):
        post_response = self.client.post(reverse('get_create_note'),
                                         data=json.dumps(self.data),
                                         headers={
                                             'Authorization': f'Bearer {self.token}'
                                         },
                                         content_type="application/json",
                                         )
        self.assertEqual(201, post_response.status_code)
        delete_response = self.client.delete(reverse('note-detail',
                                                     kwargs={'hash_link': post_response.data['hash_link']}),
                                             headers={
                                                 'Authorization': f'Bearer {self.token}'
                                             }
                                             )
        self.assertEqual(204, delete_response.status_code)


class StarsNoteTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = {
            'title': 'string',
            'content': 'string',
            'availability': 'public',
            'expiration': 120
        }
        cls.test_user = User.objects.create_user(username='Test User5',
                                                 password='1234',
                                                 email='1234@gmail.com')
        client = Client()
        user_response = client.post(reverse('token_obtain_pair'),
                                    data={"username": "Test User5",
                                          "password": "1234"},
                                    content_type="application/json",
                                    )
        cls.token = user_response.data['access']
        cls.post_response = client.post(reverse('get_create_note'),
                                        data=cls.data,
                                        headers={
                                            'Authorization': f'Bearer {cls.token}'
                                        },
                                        content_type="application/json",
                                        )
        cls.hash_link = cls.post_response.data['hash_link']

    @classmethod
    def tearDownClass(cls):
        def delete_user():
            cls.test_user.delete()

        transaction.on_commit(delete_user)
        s3_storage.delete_object(str(cls.post_response.data['key_for_s3']))

    def test_complex_stars(self):
        post_response = self.client.post(reverse('add_star',
                                                 kwargs={'hash_link': self.hash_link}),
                                         headers={
                                             'Authorization': f'Bearer {self.token}'
                                         }
                                         )
        self.assertEqual(201, post_response.status_code)
        self.assertEqual(self.data['title'], post_response.data['save_to_stars'])

        get_response = self.client.get(reverse('my_stars'),
                                       headers={
                                           'Authorization': f'Bearer {self.token}'
                                       }
                                       )
        self.assertEqual(1, len(get_response.data['my_stars']))

        delete_response = self.client.delete(reverse('delete_star',
                                                     kwargs={'hash_link': self.hash_link}),
                                             headers={
                                                 'Authorization': f'Bearer {self.token}'
                                             })
        self.assertEqual(204, delete_response.status_code)


class RatingNotesTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = {
            'title': 'string',
            'content': 'string',
            'availability': 'public',
            'expiration': 120
        }
        cls.test_user = User.objects.create_user(username='Test User6',
                                                 password='1234',
                                                 email='1234@gmail.com')
        client = Client()
        user_response = client.post(reverse('token_obtain_pair'),
                                    data={"username": "Test User6",
                                          "password": "1234"},
                                    content_type="application/json",
                                    )
        cls.token = user_response.data['access']
        cls.post_response = client.post(reverse('get_create_note'),
                                        data=cls.data,
                                        headers={
                                            'Authorization': f'Bearer {cls.token}'
                                        },
                                        content_type="application/json",
                                        )
        cls.hash_link = cls.post_response.data['hash_link']

    @classmethod
    def tearDownClass(cls):
        def delete_user():
            cls.test_user.delete()

        transaction.on_commit(delete_user)
        s3_storage.delete_object(str(cls.post_response.data['key_for_s3']))

    def get_note_rate(self):
        response = self.client.get(reverse('like_or_get_note',
                                           kwargs={'hash_link': self.hash_link}))
        return response

    def test_like_note(self):
        clean_get = self.get_note_rate()
        self.assertEqual(200, clean_get.status_code)
        self.assertEqual(0, clean_get.data['likes'])
        post_response = self.client.post(reverse('like_or_get_note',
                                                 kwargs={'hash_link': self.hash_link}),
                                         headers={
                                             'Authorization': f'Bearer {self.token}'
                                         })
        self.assertEqual(200, post_response.status_code)
        after_response = self.get_note_rate()
        self.assertEqual(1, after_response.data['likes'])

        cancel_response = self.client.post(reverse('cancel_like_note',
                                                   kwargs={'hash_link': self.hash_link}),
                                           headers={
                                               'Authorization': f'Bearer {self.token}'
                                           }
                                           )
        self.assertEqual(200, cancel_response.status_code)
        after_cancel = self.get_note_rate()
        self.assertEqual(0, after_cancel.data['likes'])


class CommentsTests(APITestCase):
    def setUp(self):
        self.data = {
            'title': 'string',
            'content': 'string',
            'availability': 'public',
            'expiration': 120
        }
        self.comment_data = {
            'body': 'nice'
        }
        self.test_user = User.objects.create_user(username='Test User6',
                                                  password='1234',
                                                  email='1234@gmail.com')
        client = Client()
        user_response = client.post(reverse('token_obtain_pair'),
                                    data={"username": "Test User6",
                                          "password": "1234"},
                                    content_type="application/json",
                                    )
        self.token = user_response.data['access']
        self.post_response = client.post(reverse('get_create_note'),
                                         data=self.data,
                                         headers={
                                             'Authorization': f'Bearer {self.token}'
                                         },
                                         content_type="application/json",
                                         )
        self.hash_link = self.post_response.data['hash_link']

    def tearDown(self):
        def delete_user():
            self.test_user.delete()

        transaction.on_commit(delete_user)
        s3_storage.delete_object(str(self.post_response.data['key_for_s3']))

    def post_comment(self):
        post_response = self.client.post(reverse('get_and_post_comment',
                                                 kwargs={'hash_link': self.hash_link}),
                                         headers={
                                             'Authorization': f'Bearer {self.token}'
                                         },
                                         data=json.dumps(self.comment_data),
                                         content_type="application/json"
                                         )
        return post_response

    def test_post_and_get_comment(self):
        post_response = self.client.post(reverse('get_and_post_comment',
                                                 kwargs={'hash_link': self.hash_link}),
                                         headers={
                                             'Authorization': f'Bearer {self.token}'
                                         },
                                         data=json.dumps(self.comment_data),
                                         content_type="application/json"
                                         )

        self.assertEqual(201, post_response.status_code)
        self.assertEqual(self.comment_data['body'], post_response.data['body'])

        get_response = self.client.get(reverse('get_and_post_comment',
                                               kwargs={'hash_link': self.hash_link}))
        self.assertEqual(200, get_response.status_code)
        self.assertIsInstance(get_response.data, list)
        self.assertEqual(self.comment_data['body'], get_response.data[0]['body'])

    def test_patch_comment(self):
        post_comment = self.post_comment()
        self.assertEqual(201, post_comment.status_code)

        patch_response = self.client.patch(reverse('patch_and_delete_comment',
                                                   kwargs={
                                                       'hash_link': self.hash_link,
                                                       'note_comment_id': post_comment.data['id']
                                                   }),
                                           headers={
                                               'Authorization': f'Bearer {self.token}'
                                           },
                                           data=json.dumps({'body': 'patch comment'}),
                                           content_type="application/json"
                                           )
        self.assertEqual(201, patch_response.status_code)
        self.assertEqual('patch comment', patch_response.data['body'])
