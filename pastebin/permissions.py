from rest_framework import permissions


class IsOwnerOrReadOnlyPublic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if obj.user != request.user and obj.availability == 'private':
                return False
            return True
        return obj.user == request.user


class IsOwnerOrReadOnlyComments(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if obj.user != request.user:
                return False
            return True
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
