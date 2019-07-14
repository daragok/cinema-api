import unittest

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.test import APITestCase

from main.models import Movie


class HasAdmin:
    def __init__(self):
        self.admin_username = 'admin'
        self.admin_email = 'admin@example.com'
        self.admin_password = 'adminpassword'
        self.admin = User.objects.create_superuser(self.admin_username, self.admin_email, self.admin_password)

    def _log_in_admin(self, client):
        client.login(username=self.admin_username, password=self.admin_password)


class HasUser:
    def __init__(self):
        self.username = 'user'
        self.user_email = 'user@example.com'
        self.user_password = 'userpassword'
        self.user = User.objects.create_user(self.username, self.user_email, self.user_password)

    def _log_in_user(self, client):
        client.login(username=self.username, password=self.user_password)


class AccountsTest(APITestCase, HasUser, HasAdmin):
    def setUp(self):
        HasUser.__init__(self)
        HasAdmin.__init__(self)
        self.foobar_email = 'foobar@example.com'
        self.foobar_username = 'foobar'
        self.foobar_password = 'foobarfoobar'

        self.get_list_url = reverse('accounts-list')
        self.get_admin_detail_url = reverse('accounts-detail', kwargs={'pk': self.admin.pk})
        self.get_user_detail_url = reverse('accounts-detail', kwargs={'pk': self.user.pk})
        self.create_url = reverse('accounts-list')
        self.patch_admin_detail_url = reverse('accounts-detail', kwargs={'pk': self.admin.pk})
        self.patch_user_detail_url = reverse('accounts-detail', kwargs={'pk': self.user.pk})

    def test_create_user(self):
        data = {
            'username': self.foobar_username,
            'email': self.foobar_email,
            'password': self.foobar_password
        }

        response = self.client.post(self.create_url, data)

        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], data['email'])
        self.assertEqual(response.data['username'], data['username'])
        self.assertFalse('password' in response.data)

    def test_create_user_with_short_password(self):
        data = {
            'username': self.foobar_username,
            'email': self.foobar_email,
            'password': 'foobar'
        }

        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data['password']), 1)
        self.assertEqual(str(response.data['password'][0]), 'Ensure this field has at least 8 characters.')

    def test_create_user_with_no_password(self):
        data = {
            'username': self.foobar_username,
            'email': self.foobar_email,
            'password': ''
        }

        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data['password']), 1)
        self.assertEqual(str(response.data['password'][0]), 'This field may not be blank.')

    def test_create_user_with_no_username(self):
        data = {
            'username': '',
            'email': self.foobar_email,
            'password': self.foobar_password
        }

        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data['username']), 1)
        self.assertEqual(str(response.data['username'][0]), 'This field may not be blank.')

    def test_create_user_with_too_long_username(self):
        data = {
            'username': 'f' * 33,
            'email': self.foobar_email,
            'password': self.foobar_password
        }

        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data['username']), 1)
        self.assertEqual(str(response.data['username'][0]), 'Ensure this field has no more than 32 characters.')

    def test_create_user_with_preexisting_email(self):
        data = {
            'username': self.foobar_username,
            'email': 'user@example.com',
            'password': self.foobar_password
        }

        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data['email']), 1)
        self.assertEqual(str(response.data['email'][0]), 'This field must be unique.')

    def test_create_user_with_invalid_email(self):
        data = {
            'username': self.foobar_username,
            'email': 'invalid_email',
            'password': self.foobar_password
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data['email']), 1)
        self.assertEqual(str(response.data['email'][0]), 'Enter a valid email address.')

    def test_create_user_with_no_email(self):
        data = {
            'username': self.foobar_username,
            'email': '',
            'password': self.foobar_password
        }

        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data['email']), 1)
        self.assertEqual(str(response.data['email'][0]), 'This field may not be blank.')

    def test_admin_gets_all_users_list(self):
        self._log_in_admin(self.client)
        response = self.client.get(self.get_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_admin_gets_user_detail(self):
        self._log_in_admin(self.client)
        response = self.client.get(self.get_user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.username)

    def test_user_gets_user_detail(self):
        self._log_in_admin(self.client)
        response = self.client.get(self.get_user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.username)

    def test_user_gets_admin_detail(self):
        self._log_in_user(self.client)
        response = self.client.get(self.get_admin_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')

    def test_user_gets_users_list(self):
        self._log_in_user(self.client)
        response = self.client.get(self.get_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data['detail']), 'You do not have permission to perform this action.')

    def test_admin_updates_user(self):
        self._log_in_admin(self.client)
        new_username = 'new_username'
        data = {'username': new_username}
        response = self.client.patch(self.patch_user_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], new_username)
        self.assertEqual(response.data['email'], self.user_email)

    def test_user_updates_self_username(self):
        self._log_in_user(self.client)
        new_username = 'new_username'
        data = {'username': new_username}
        response = self.client.patch(self.patch_user_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], new_username)
        self.assertEqual(response.data['email'], self.user_email)

    def test_user_updates_self_password(self):
        self._log_in_user(self.client)
        new_password = 'new_password'
        data = {
            'password': new_password,
        }
        response = self.client.patch(self.patch_user_detail_url, data)
        user = get_object_or_404(User, pk=self.user.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user.check_password(new_password))
        self.assertNotIn('password', response.data)

    def test_user_updates_another(self):
        self._log_in_user(self.client)
        new_username = 'new_username'
        data = {'username': new_username}
        response = self.client.patch(self.patch_admin_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data['detail']), 'You do not have permission to perform this action.')

    def test_user_creates_user(self):
        self._log_in_user(self.client)
        data = {
            'username': self.foobar_username,
            'email': self.foobar_email,
            'password': self.foobar_password
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data['detail']), 'You do not have permission to perform this action.')

    def test_admin_creates_user(self):
        self._log_in_admin(self.client)
        data = {
            'username': self.foobar_username,
            'email': self.foobar_email,
            'password': self.foobar_password
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], data['username'])


class TheaterRoomTest(APITestCase):
    def setUp(self):
        self.list_url = reverse('theater-room-list')

    def test_list_theater_rooms(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_theater_room(self):
        data = {}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data['detail']), 'Method "POST" not allowed.')

    def test_update_theater_room(self):
        data = {}
        response = self.client.put(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data['detail']), 'Method "PUT" not allowed.')

    def test_delete_theater_room(self):
        data = {}
        response = self.client.delete(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data['detail']), 'Method "DELETE" not allowed.')


class MovieTest(APITestCase, HasUser, HasAdmin):
    def setUp(self):
        HasUser.__init__(self)
        HasAdmin.__init__(self)

        self.movie_hp = Movie.objects.create(title="Harry Potter and the Philosopher's Stone", duration_minutes=159)
        self.movie_sw = Movie.objects.create(title="Episode IV: A New Hope", duration_minutes=125)

        self.list_url = reverse('movies-list')
        self.detail_url_hp_movie = reverse('movies-detail', kwargs={'pk': self.movie_hp.pk})

    def test_list_movies_anon(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_movie_anon(self):
        response = self.client.get(self.detail_url_hp_movie)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.movie_hp.title)
        self.assertEqual(response.data['duration_minutes'], self.movie_hp.duration_minutes)

    def test_update_movie_anon(self):
        data = {'duration_minutes': 160}
        response = self.client.patch(self.detail_url_hp_movie, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_movie_anon(self):
        response = self.client.delete(self.detail_url_hp_movie)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_movie_admin(self):
        self._log_in_admin(self.client)
        data = {'title': "The Lion King", "duration_minutes": 118}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 3)

    def test_create_movie_admin_duration_too_short(self):
        self._log_in_admin(self.client)
        data = {'title': "The Lion King", "duration_minutes": -1}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data['duration_minutes']), 1)
        self.assertEqual(str(response.data['duration_minutes'][0]), 'Ensure this value is greater than or equal to 10.')

    def test_create_movie_admin_title_too_long(self):
        self._log_in_admin(self.client)
        data = {'title': "T" * 101, "duration_minutes": 118}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data['title']), 1)
        self.assertEqual(str(response.data['title'][0]), 'Ensure this field has no more than 100 characters.')

    def test_create_movie_admin_duration_too_long(self):
        self._log_in_admin(self.client)
        data = {'title': "The Lion King", "duration_minutes": 501}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data['duration_minutes']), 1)
        self.assertEqual(str(response.data['duration_minutes'][0]),
                         'Ensure this value is less than or equal to 500.')

    def test_update_movie_admin_no_screening(self):
        self._log_in_admin(self.client)
        new_duration = 160
        data = {'duration_minutes': new_duration}
        response = self.client.patch(self.detail_url_hp_movie, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.movie_hp.title)
        self.assertEqual(response.data['duration_minutes'], new_duration)

    @unittest.skip('requires Screening implementation')
    def test_update_movie_admin_with_screening(self):
        pass

    def test_delete_movie_admin_no_screening(self):
        self._log_in_admin(self.client)
        response = self.client.delete(self.detail_url_hp_movie)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @unittest.skip('requires Screening implementation')
    def test_delete_movie_admin_with_screening(self):
        pass

    # restricted actions to normal user
    def test_create_movie_user(self):
        self._log_in_user(self.client)
        data = {'title': "The Lion King", "duration_minutes": 118}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')

    def test_update_movie_user(self):
        self._log_in_user(self.client)
        data = {'duration_minutes': 160}
        response = self.client.patch(self.detail_url_hp_movie, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')

    def test_delete_movie_user(self):
        self._log_in_user(self.client)
        response = self.client.delete(self.detail_url_hp_movie)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')
