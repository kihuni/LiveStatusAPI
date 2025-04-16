from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Admins can access any presence
        if request.user and request.user.is_staff:
            return True

        # Otherwise, only allow access if the user owns the presence
        return obj.user == request.user
