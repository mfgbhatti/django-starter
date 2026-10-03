from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

User = get_user_model()

PASSWORD = "correct-horse-battery-9"


class UserModelTests(TestCase):
    def test_email_is_the_username_field(self):
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_create_user_keeps_username_and_lowercases_email(self):
        user = User.objects.create_user(
            username="ada", email="  Ada@Example.COM ", password=PASSWORD
        )
        self.assertEqual(user.username, "ada")
        self.assertEqual(user.email, "ada@example.com")
        self.assertTrue(user.check_password(PASSWORD))

    def test_email_is_unique_regardless_of_case(self):
        User.objects.create_user(username="a", email="a@example.com", password=PASSWORD)
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(
                username="b", email="A@example.com", password=PASSWORD
            )

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username="root", email="root@example.com", password=PASSWORD
        )
        self.assertTrue(admin.is_staff and admin.is_superuser)


@override_settings(SECURE_SSL_REDIRECT=False)
class AuthFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="ada", email="ada@example.com", password=PASSWORD
        )

    def login(self, email="ada@example.com", password=PASSWORD):
        return self.client.post(
            reverse("accounts:login"), {"username": email, "password": password}
        )

    def test_login_page_renders(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, 'type="email"')

    def test_login_with_email_redirects_home(self):
        response = self.login()
        self.assertRedirects(response, "/")

    def test_login_email_is_case_insensitive(self):
        self.assertRedirects(self.login(email="ADA@Example.com"), "/")

    def test_login_with_username_is_rejected(self):
        response = self.login(email="ada")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_wrong_password(self):
        response = self.login(password="nope")
        self.assertContains(response, "Please enter a correct")

    def test_deactivated_account_gets_distinct_message(self):
        User.objects.filter(pk=self.user.pk).update(is_active=False)
        response = self.login()
        self.assertContains(response, "inactive")

    def test_deactivated_account_with_wrong_password_stays_generic(self):
        User.objects.filter(pk=self.user.pk).update(is_active=False)
        response = self.login(password="nope")
        self.assertNotContains(response, "inactive")
        self.assertContains(response, "Please enter a correct")

    def test_home_requires_login(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/accounts/login/?next=/")

    def test_logout_is_post_only_and_redirects_to_login(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)


@override_settings(SECURE_SSL_REDIRECT=False)
class AdminTests(TestCase):
    def test_admin_add_user_form_works(self):
        admin = User.objects.create_superuser(
            username="root", email="root@example.com", password=PASSWORD
        )
        self.client.force_login(admin)
        url = reverse("admin:accounts_baseuser_add")
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post(
            url,
            {
                "email": "new@example.com",
                "username": "new",
                "usable_password": "true",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())
        self.assertEqual(
            self.client.get(reverse("admin:accounts_baseuser_changelist")).status_code,
            200,
        )
