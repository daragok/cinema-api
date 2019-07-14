from datetime import timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.test import APITestCase

from main.models import Movie, Screening, TheaterRoom

USERNAME = 'user'
USER_EMAIL = 'user@example.com'

ADMIN_USERNAME = 'admin'


class AccountsTest(APITestCase):
    fixtures = ['user.json', 'admin.json']

    def setUp(self):
        self.foobar_email = 'foobar@example.com'
        self.foobar_username = 'foobar'
        self.foobar_password = 'foobarfoobar'

        self.admin = User.objects.get(username=ADMIN_USERNAME)
        self.user = User.objects.get(username=USERNAME)

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
        self.client.force_login(self.admin)
        response = self.client.get(self.get_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_admin_gets_user_detail(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.get_user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], USERNAME)

    def test_user_gets_user_detail(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.get_user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], USERNAME)

    def test_user_gets_admin_detail(self):
        self.client.force_login(self.user)
        response = self.client.get(self.get_admin_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')

    def test_user_gets_users_list(self):
        self.client.force_login(self.user)
        response = self.client.get(self.get_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data['detail']), 'You do not have permission to perform this action.')

    def test_admin_updates_user(self):
        self.client.force_login(self.admin)
        new_username = 'new_username'
        data = {'username': new_username}
        response = self.client.patch(self.patch_user_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], new_username)
        self.assertEqual(response.data['email'], USER_EMAIL)

    def test_user_updates_self_username(self):
        self.client.force_login(self.user)
        new_username = 'new_username'
        data = {'username': new_username}
        response = self.client.patch(self.patch_user_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], new_username)
        self.assertEqual(response.data['email'], USER_EMAIL)

    def test_user_updates_self_password(self):
        self.client.force_login(self.user)
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
        self.client.force_login(self.user)
        new_username = 'new_username'
        data = {'username': new_username}
        response = self.client.patch(self.patch_admin_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data['detail']), 'You do not have permission to perform this action.')

    def test_user_creates_user(self):
        self.client.force_login(self.user)
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
        self.client.force_login(self.admin)
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


class MovieTest(APITestCase):
    fixtures = ['user.json', 'admin.json', 'movies.json']

    def setUp(self):
        self.admin = User.objects.get(username=ADMIN_USERNAME)
        self.user = User.objects.get(username=USERNAME)

        self.movie_hp = Movie.objects.get(title="Harry Potter and the Philosopher's Stone")
        self.movie_sw = Movie.objects.get(title="Episode IV: A New Hope")

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
        self.client.force_login(self.admin)
        data = {'title': "The Lion King", "duration_minutes": 118}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 3)

    def test_create_movie_admin_duration_too_short(self):
        self.client.force_login(self.admin)
        data = {'title': "The Lion King", "duration_minutes": -1}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data['duration_minutes']), 1)
        self.assertEqual(str(response.data['duration_minutes'][0]), 'Ensure this value is greater than or equal to 10.')

    def test_create_movie_admin_title_too_long(self):
        self.client.force_login(self.admin)
        data = {'title': "T" * 101, "duration_minutes": 118}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data['title']), 1)
        self.assertEqual(str(response.data['title'][0]), 'Ensure this field has no more than 100 characters.')

    def test_create_movie_admin_duration_too_long(self):
        self.client.force_login(self.admin)
        data = {'title': "The Lion King", "duration_minutes": 501}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data['duration_minutes']), 1)
        self.assertEqual(str(response.data['duration_minutes'][0]),
                         'Ensure this value is less than or equal to 500.')

    def test_update_movie_admin_no_screening(self):
        self.client.force_login(self.admin)
        new_duration = 160
        data = {'duration_minutes': new_duration}
        response = self.client.patch(self.detail_url_hp_movie, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.movie_hp.title)
        self.assertEqual(response.data['duration_minutes'], new_duration)

    def test_update_movie_admin_with_screening(self):
        self._add_screening()
        self.client.force_login(self.admin)
        new_duration = 160
        data = {'duration_minutes': new_duration}
        response = self.client.patch(self.detail_url_hp_movie, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'The movie cannot be updated while it is in screenings')

    def test_delete_movie_admin_no_screening(self):
        self.client.force_login(self.admin)
        response = self.client.delete(self.detail_url_hp_movie)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_movie_admin_with_screening(self):
        self._add_screening()
        self.client.force_login(self.admin)
        response = self.client.delete(self.detail_url_hp_movie)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'The movie cannot be deleted while it is in screenings')

    # restricted actions to normal user
    def test_create_movie_user(self):
        self.client.force_login(self.user)
        data = {'title': "The Lion King", "duration_minutes": 118}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')

    def test_update_movie_user(self):
        self.client.force_login(self.user)
        data = {'duration_minutes': 160}
        response = self.client.patch(self.detail_url_hp_movie, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')

    def test_delete_movie_user(self):
        self.client.force_login(self.user)
        response = self.client.delete(self.detail_url_hp_movie)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')

    def _add_screening(self):
        Screening.objects.create(
            room=TheaterRoom.objects.all()[0], movie=self.movie_hp, start_time=timezone.now(), price=100
        )


class ScreeningTest(APITestCase):
    fixtures = ['user.json', 'admin.json', 'movies.json', 'screenings.json']

    def setUp(self):
        self.admin = User.objects.get(username=ADMIN_USERNAME)
        self.user = User.objects.get(username=USERNAME)

        self.list_url = reverse('screenings-list')
        self.detail_url = reverse('screenings-detail', kwargs={'pk': 1})

    def test_list_screenings_anon(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_screening_admin(self):
        self.client.force_login(self.admin)
        datetime = timezone.datetime(2020, 1, 1, 12, 0, 0)
        data = {
            "room": 1,
            "movie": 2,
            "start_time": datetime,
            "price": 200

        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_screening_price_too_small(self):
        self.client.force_login(self.admin)
        datetime = timezone.datetime(2020, 1, 1, 12, 0, 0)
        data = {
            "room": 1,
            "movie": 2,
            "start_time": datetime,
            "price": -1

        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data['price']), 1)
        self.assertEqual(response.data['price'][0], 'Ensure this value is greater than or equal to 1.')

    def test_create_non_intersecting_screenings_admin(self):
        self.client.force_login(self.admin)
        movie_screening = Screening.objects.get(pk=2)
        # movie 2 has duration of 125 min + 10 min for ads + 15 min for cleaning = 150 min
        next_movie_start_datetime = movie_screening.start_time + timedelta(minutes=151)
        data = {
            "room": movie_screening.room.pk,
            "movie": movie_screening.movie.pk,
            "start_time": next_movie_start_datetime,
            "price": 200
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_intersecting_screenings_starts_within(self):
        self.client.force_login(self.admin)
        movie_screening = Screening.objects.get(pk=2)
        # movie in screening with pk 2 has duration of 125 min + 10 min for ads + 15 min for cleaning = 150 min
        next_movie_start_datetime = movie_screening.start_time + timedelta(minutes=149)
        data = {
            "room": movie_screening.room.pk,
            "movie": movie_screening.movie.pk,
            "start_time": next_movie_start_datetime,
            "price": 200
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['start_time'][0], 'Screenings should not intersect.')

    def test_create_intersecting_screenings_ends_within(self):
        self.client.force_login(self.admin)
        movie_screening = Screening.objects.get(pk=2)
        # movie in screening with pk 2 has duration of 125 min + 10 min for ads + 15 min for cleaning = 150 min
        prev_movie_start_datetime = movie_screening.start_time - timedelta(minutes=149)
        data = {
            "room": movie_screening.room.pk,
            "movie": movie_screening.movie.pk,
            "start_time": prev_movie_start_datetime,
            "price": 200
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['start_time'][0], 'Screenings should not intersect.')

    def test_create_intersecting_screenings_start_before_ends_after(self):
        self.client.force_login(self.admin)
        movie_screening = Screening.objects.get(pk=2)
        # movie in screening with pk 2 has duration of 125 min + 10 min for ads + 15 min for cleaning = 150 min
        prev_movie_start_datetime = movie_screening.start_time - timedelta(minutes=149)
        # movie starts before the new one. Movie with pk 1 has longer duration, so it ends after the new one
        data = {
            "room": movie_screening.room.pk,
            "movie": 1,
            "start_time": prev_movie_start_datetime,
            "price": 200
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['start_time'][0], 'Screenings should not intersect.')

    def test_create_screening_too_early_in_the_morning(self):
        self.client.force_login(self.admin)
        datetime = timezone.datetime(2020, 1, 1, 7, 59, 59)
        data = {
            "room": 1,
            "movie": 2,
            "start_time": datetime,
            "price": 200

        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['start_time'][0], 'Screening cannot start before 8am.')

    def test_create_screening_too_late_at_night(self):
        self.client.force_login(self.admin)
        datetime = timezone.datetime(2020, 1, 1, 23, 0, 1)
        data = {
            "room": 1,
            "movie": 2,
            "start_time": datetime,
            "price": 200

        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['start_time'][0], 'Screening cannot start later than 11pm.')

    def test_update_screening_admin(self):
        self.client.force_login(self.admin)
        new_price = 200
        data = {"price": new_price}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['price'], new_price)

    def test_update_screening_admin_intersection(self):
        self.client.force_login(self.admin)
        existing_screening = Screening.objects.get(pk=2)
        data = {
            "room": existing_screening.room.pk,
            "movie": existing_screening.movie.pk,
            "start_time": existing_screening.start_time + timedelta(minutes=10),
            "price": 200
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['start_time'][0], 'Screenings should not intersect.')

    def test_delete_screening_admin(self):
        self.client.force_login(self.admin)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_screening_user(self):
        self.client.force_login(self.user)
        response = self.client.post(self.list_url, data={})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_screening_user(self):
        self.client.force_login(self.user)
        response = self.client.patch(self.detail_url, data={})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_screening_user(self):
        self.client.force_login(self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
