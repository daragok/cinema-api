from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from main import permissions as custom_permissions
from main.models import TheaterRoom, Movie, Screening
from main.serializers import UserSerializer, TheaterRoomSerializer, MovieSerializer, ScreeningSerializer


class UserView(viewsets.ModelViewSet):
    permission_classes = (custom_permissions.RetrieveUpdateSelfOnlyOrAdmin,
                          custom_permissions.CreateAnonymousOrAdmin,
                          custom_permissions.ListAdminOnly)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TheaterRoomListView(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin):
    queryset = TheaterRoom.objects.all()
    serializer_class = TheaterRoomSerializer


class MovieViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except models.deletion.ProtectedError:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'detail': 'The movie cannot be deleted while it is in screenings'})

    def update(self, request, *args, **kwargs):
        return call_method_catch_protected_error(super().update, request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return call_method_catch_protected_error(super().partial_update, request, *args, **kwargs)


def call_method_catch_protected_error(method, request, *args, **kwargs):
    try:
        return method(request, *args, **kwargs)
    except models.deletion.ProtectedError as e:
        obj, message = e.args
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': message})


class ScreeningViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)

    queryset = Screening.objects.all()
    serializer_class = ScreeningSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'detail': e.args[0]})
