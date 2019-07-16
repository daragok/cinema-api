from datetime import timedelta

from django.contrib.auth.models import User
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
    price = serializers.IntegerField(min_value=1)
    available_seats = serializers.HyperlinkedIdentityField(view_name='available-seats')

    class Meta:
        model = Screening
        fields = ('id', 'room', 'movie', 'start_time', 'price', 'available_seats')

    def validate(self, attrs):
        if 'start_time' in attrs:
            self._validate(attrs)
        return super().validate(attrs)

    def _validate(self, validated_data):
        new_start = validated_data['start_time']
        if new_start.time().hour < 8:
            raise serializers.ValidationError({'start_time': 'Screening cannot start before 8am.'})
        latest_allowed_start_time = timezone.datetime(1, 1, 1, 23, 0, 0).time()
        if new_start.time() > latest_allowed_start_time:
            raise serializers.ValidationError({'start_time': 'Screening cannot start later than 11pm.'})
        new_end = new_start + timedelta(minutes=validated_data['movie'].duration_minutes + Screening.IDLE_TIME)
        screens_start_same_day = Screening.objects.filter(
            room_id__exact=validated_data['room'].pk,
            start_time__year=new_start.year, start_time__month=new_start.month,
            start_time__day=new_start.day
        )
        for s in screens_start_same_day:
            if new_start < s.start_time < new_end \
                    or new_start < s.end_time < new_end \
                    or s.start_time < new_start < s.end_time:
                raise serializers.ValidationError({'start_time': "Screenings should not intersect."})
