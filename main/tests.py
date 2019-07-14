from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AccountsTest(APITestCase):
    def setUp(self):
        self.admin_username = 'admin'
        self.admin_email = 'admin@example.com'
        self.admin_password = 'adminpassword'
        self.admin = User.objects.create_superuser(self.admin_username, self.admin_email, self.admin_password)

        self.username = 'user'
        self.user_email = 'user@example.com'
        self.user_password = 'userpassword'
        self.user = User.objects.create_user(self.username, self.user_email, self.user_password)

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
        self._log_in_admin()
        response = self.client.get(self.get_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_admin_gets_user_detail(self):
        self._log_in_admin()
        response = self.client.get(self.get_user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.username)

    def test_user_gets_user_detail(self):
        self._log_in_user()
        response = self.client.get(self.get_user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.username)

    def test_user_gets_admin_detail(self):
        self._log_in_user()
        response = self.client.get(self.get_admin_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')

    def test_user_gets_users_list(self):
        self._log_in_user()
        response = self.client.get(self.get_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data['detail']), 'You do not have permission to perform this action.')

    def test_admin_updates_user(self):
        self._log_in_admin()
        new_username = 'new_username'
        data = {'username': new_username}
        response = self.client.patch(self.patch_user_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], new_username)
        self.assertEqual(response.data['email'], self.user_email)

    def test_user_updates_himself(self):
        self._log_in_user()
        new_username = 'new_username'
        data = {'username': new_username}
        response = self.client.patch(self.patch_user_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], new_username)
        self.assertEqual(response.data['email'], self.user_email)

    def test_user_updates_another(self):
        self._log_in_user()
        new_username = 'new_username'
        data = {'username': new_username}
        response = self.client.patch(self.patch_admin_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data['detail']), 'You do not have permission to perform this action.')

    def test_user_creates_user(self):
        self._log_in_user()
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
        self._log_in_admin()
        data = {
            'username': self.foobar_username,
            'email': self.foobar_email,
            'password': self.foobar_password
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], data['username'])

    def _log_in_admin(self):
        self.client.login(username=self.admin_username, password=self.admin_password)

    def _log_in_user(self):
        self.client.login(username=self.username, password=self.user_password)
