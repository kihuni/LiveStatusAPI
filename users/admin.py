from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role

class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'priority', 'created_at')
    search_fields = ('name',)
    ordering = ('-priority',)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'full_name', 'role', 'is_active', 'is_staff', 'email_verified')
    list_filter = ('is_staff', 'is_active', 'role', 'email_verified')
    search_fields = ('email', 'username', 'full_name')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'full_name', 'avatar', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Role & Status', {'fields': ('role', 'is_online', 'email_verified', 'last_seen', 'date_joined')}),
        ('Verification', {'fields': ('verification_token', 'verification_token_created')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(Role, RoleAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
