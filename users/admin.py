from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Role, CustomUser

# Get the user actual user model we are using for our project
CustomUser = get_user_model()


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):

    list_display = ('id', 'username', 'email', 'email_verified',
                    'full_name', 'is_staff', 'is_online', 'last_seen')
    list_editable = ('username', 'email',
                     'full_name', 'is_online', 'is_staff', 'is_staff')
    list_filter = ('username', 'email')
    list_per_page = 10  # applies pagination

    # any words entered into the search box will be searched from this fields e.g username ='what was entered into search box'
    search_fields = ('username', 'full_name', 'device_tokens')

    class Meta:
        model = CustomUser
        fields = "__all__"


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'priority', 'custom_permissions', 'can_moderate',
              'can_manage_users', 'can_manage_roles', 'can_delete_messages', 'can_ban_users')
    list_display = ('id', 'name', 'priority', 'custom_permissions', 'can_moderate',
                    'can_manage_users', 'can_manage_roles', 'can_delete_messages', 'can_ban_users')
    list_editable = ('name', 'priority')
    list_filter = ('priority',)
    list_per_page = 10
    search_fields = ('name', 'priority')

