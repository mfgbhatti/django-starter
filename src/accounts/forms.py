from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    AdminUserCreationForm,
    AuthenticationForm,
    UserChangeForm,
)
from django.core.exceptions import ValidationError

from .models import BaseUser

User = get_user_model()


class BaseUserCreationForm(AdminUserCreationForm):
    class Meta(AdminUserCreationForm.Meta):
        model = BaseUser
        fields = ("email", "username")


class BaseUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = BaseUser
        fields = "__all__"


class BaseUserLoginForm(AuthenticationForm):
    """Email + password login that flags a deactivated account distinctly.

    The "deactivated" message is only shown when the password is correct, so
    it doesn't reveal which emails have accounts.
    """

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}),
    )

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                candidate = User._default_manager.filter(
                    **{User.USERNAME_FIELD: username}
                ).first()
                if (
                    candidate
                    and not candidate.is_active
                    and candidate.check_password(password)
                ):
                    raise ValidationError(
                        self.error_messages["inactive"], code="inactive"
                    )
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
