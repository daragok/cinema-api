from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from main.models import TheaterRoom, Movie, Screening


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        max_length=32,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = super().create(validated_data)
        # set password correctly to create hash
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        if 'password' in validated_data:
            # set password correctly to create hash
            user.set_password(validated_data['password'])
            user.save()
        return user


class TheaterRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheaterRoom
        fields = ('id', 'name', 'rows_count', 'seats_per_row_count')


class MovieSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=Movie.TITLE_MAX_LENGTH)
    duration_minutes = serializers.IntegerField(min_value=10, max_value=500)

    class Meta:
        model = Movie
        fields = ('id', 'title', 'duration_minutes')

    def update(self, instance, validated_data):
        screenings = Screening.objects.filter(movie=instance)
        if screenings:
            raise models.deletion.ProtectedError(instance, 'The movie cannot be updated while it is in screenings')
        return super().update(instance, validated_data)


class ScreeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screening
        fields = ('id', 'room', 'movie', 'start_time', 'price')

    def create(self, validated_data):
        latest_allowed_start_time = timezone.datetime(2000, 1, 1, 23, 0, 0).time()
        if validated_data['start_time'].time().hour < 8:
            raise ValidationError('Screening cannot start before 8am.')
        if validated_data['start_time'].time() > latest_allowed_start_time:
            raise ValidationError('Screening cannot start later than 11pm.')
        return super().create(validated_data)
