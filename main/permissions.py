from rest_framework import permissions


class RetrieveUpdateSelfOnlyOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return view.action in ['retrieve', 'update',
                               'partial_update'] and obj.id == request.user.id or request.user.is_staff


class CreateAnonymousOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return view.action != 'create' or request.user.is_staff or view.action == 'create' and request.user.is_anonymous


class ListAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff or view.action != 'list'
