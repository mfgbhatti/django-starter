from django.test import Client
from django.urls import reverse

from .test_base import PASSWORD, AccountsTestCase, User


class LoginViewTests(AccountsTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = cls.make_user()
        cls.url = reverse("accounts:login")

    def login(self, email="ada@example.com", password=PASSWORD, **extra):
        return self.client.post(self.url, {"username": email, "password": password, **extra})

    def test_page_renders_with_an_email_field(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertContains(response, 'type="email"')
        self.assertContains(response, 'type="password"')
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_success_logs_in_and_redirects_to_login_redirect_url(self):
        response = self.login()
        self.assertRedirects(response, "/")
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_email_is_case_insensitive(self):
        self.assertRedirects(self.login(email="ADA@example.COM"), "/")

    def test_next_is_followed_when_it_is_local(self):
        response = self.login(next="/admin/")
        self.assertRedirects(response, "/admin/", fetch_redirect_response=False)

    def test_next_to_another_host_is_ignored(self):
        response = self.login(next="https://evil.example.com/")
        self.assertRedirects(response, "/")

    def test_username_cannot_be_used_to_log_in(self):
        response = self.login(email="ada")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_wrong_password_shows_a_generic_error(self):
        response = self.login(password="nope")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct email address and password")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_unknown_email_shows_the_same_generic_error(self):
        response = self.login(email="nobody@example.com")
        self.assertContains(response, "Please enter a correct email address and password")

    def test_deactivated_account_gets_its_own_message(self):
        User.objects.filter(pk=self.user.pk).update(is_active=False)
        response = self.login()
        self.assertContains(response, "inactive")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_deactivated_account_with_wrong_password_does_not_leak(self):
        User.objects.filter(pk=self.user.pk).update(is_active=False)
        response = self.login(password="nope")
        self.assertNotContains(response, "inactive")

    def test_already_logged_in_users_are_redirected_away(self):
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get(self.url), "/")

    def test_csrf_token_is_enforced(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(self.url, {"username": "ada@example.com", "password": PASSWORD})
        self.assertEqual(response.status_code, 403)

    def test_login_creates_a_session_that_expires_with_the_browser(self):
        self.login()
        self.assertTrue(self.client.session.get_expire_at_browser_close())


class LogoutViewTests(AccountsTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = cls.make_user()
        cls.url = reverse("accounts:logout")

    def test_post_logs_out_and_redirects_to_login(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_get_is_not_allowed(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

    def test_anonymous_post_is_harmless(self):
        self.assertRedirects(self.client.post(self.url), reverse("accounts:login"))

    def test_csrf_token_is_enforced(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(self.url).status_code, 403)
        self.assertIn("_auth_user_id", client.session)


class UrlTests(AccountsTestCase):
    def test_urls(self):
        self.assertEqual(reverse("accounts:login"), "/accounts/login/")
        self.assertEqual(reverse("accounts:logout"), "/accounts/logout/")

    def test_login_required_pages_send_anonymous_users_to_login(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/accounts/login/?next=/")
