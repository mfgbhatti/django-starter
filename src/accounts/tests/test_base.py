from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

User = get_user_model()

PASSWORD = "correct-horse-battery-9"


@override_settings(SECURE_SSL_REDIRECT=False)
class AccountsTestCase(TestCase):
    """Base class: HTTP test client without the production HTTPS redirect."""

    @classmethod
    def make_user(cls, email="ada@example.com", username="ada", **extra):
        return User.objects.create_user(
            username=username, email=email, password=PASSWORD, **extra
        )

    @classmethod
    def make_superuser(cls, email="root@example.com", username="root"):
        return User.objects.create_superuser(
            username=username, email=email, password=PASSWORD
        )
