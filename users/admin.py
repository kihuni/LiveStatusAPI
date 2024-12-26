from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Role

# Register your models here.

# Get the user actual user model we are using for our project
CustomUser = get_user_model()


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):

    # fields specified will be used to capture details to be stored
    fields = ('username', 'email', 'full_name', 'avatar', 'bio', 'is_online', 'last_seen', 'device_tokens', 'role',
              'email_verified', 'verification_token', 'verification_token_created', 'date_joined', 'is_active', 'is_staff')

    list_display = ('id', 'username', 'email', 'email_verified',
                    'full_name','is_staff', 'is_online', 'last_seen')
    list_editable = ('username', 'email',
                     'full_name', 'is_online','is_staff' ,'is_staff')
    list_filter = ('username', 'email')
    list_per_page = 10 # applies pagination

    # any words entered into the search box will be searched from this fields e.g username ='what was entered into search box'
    search_fields = ('username', 'full_name', 'device_tokens')
