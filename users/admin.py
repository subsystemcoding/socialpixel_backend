from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile
from django.utils.translation import gettext_lazy as _

class UserAdminConfig(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide', 'extrapretty'),
            'fields': ('first_name','last_name', 'email', 'username', 'password1', 'password2'),
        }),
    )
    readonly_fields = [
        'date_joined', 'last_login'
    ]


admin.site.register(User, UserAdminConfig)
admin.site.register(Profile)
