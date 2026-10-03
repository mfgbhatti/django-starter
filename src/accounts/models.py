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

    def save(self, *args, **kwargs):
        # Emails are stored lowercase so "A@x.com" and "a@x.com" can't both exist.
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)
