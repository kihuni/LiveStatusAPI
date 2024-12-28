from rest_framework.permissions import BasePermission

class RolePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or not user.role:
            return False
        
        # Map views to required permissions
        endpoint_permissions = {
            'manage_roles': 'can_manage_roles',
            'manage_users': 'can_manage_users',
            'moderate_chats': 'can_moderate',
            'delete_messages': 'can_delete_messages',
        }
        required_permission = endpoint_permissions.get(view.action)
        
        # Check if the user has the required permission
        return required_permission and user.get_permissions().get(required_permission, False)
