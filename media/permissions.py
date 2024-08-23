from rest_framework.permissions import BasePermission


class IsOwnerProfile(BasePermission):
    """
    Custom permission to only allow owners of a profile to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
