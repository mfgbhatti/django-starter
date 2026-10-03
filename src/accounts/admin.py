from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import BaseUserChangeForm, BaseUserCreationForm
from .models import BaseUser


@admin.register(BaseUser)
class BaseUserAdmin(UserAdmin):
    form = BaseUserChangeForm
    add_form = BaseUserCreationForm
    ordering = ("email",)
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    search_fields = ("email", "username", "first_name", "last_name")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "usable_password",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
