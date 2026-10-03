from django.contrib.auth.models import AbstractUser
from django.db import models


class BaseUser(AbstractUser):
    """Django's stock user, except that people log in with their email.

    Everything else (username, names, permissions, ...) is inherited from
    AbstractUser unchanged. `username` is kept and still required, so
    `createsuperuser` asks for both.
    """

    email = models.EmailField(
        "email address",
        unique=True,
        error_messages={"unique": "A user with that email already exists."},
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def clean(self):
        super().clean()
        # Runs inside ModelForm validation *before* the uniqueness check, so
        # "A@x.com" is reported as a duplicate of "a@x.com" instead of
        # failing later with an IntegrityError.
        self.email = (self.email or "").strip().lower()

    def save(self, *args, **kwargs):
        # Emails are stored lowercase so "A@x.com" and "a@x.com" can't both exist.
        self.email = (self.email or "").strip().lower()
        if not self.email:
            raise ValueError("A BaseUser needs an email address.")
        super().save(*args, **kwargs)
