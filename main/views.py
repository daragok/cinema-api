from django.contrib.auth.models import User
from rest_framework import viewsets

from main import permissions as custom_permissions
from main.serializers import UserSerializer


class UserView(viewsets.ModelViewSet):
    permission_classes = (custom_permissions.RetrieveUpdateSelfOnlyOrAdmin,
                          custom_permissions.CreateAnonymousOrAdmin,
                          custom_permissions.ListAdminOnly)
    queryset = User.objects.all()
    serializer_class = UserSerializer
