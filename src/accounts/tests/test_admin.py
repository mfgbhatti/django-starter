from django.urls import reverse

from .test_base import PASSWORD, AccountsTestCase, User


class BaseUserAdminTests(AccountsTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = cls.make_superuser()
        cls.ada = cls.make_user()

    def setUp(self):
        self.client.force_login(self.admin)

    def test_changelist_lists_users_by_email(self):
        response = self.client.get(reverse("admin:accounts_baseuser_changelist"))
        self.assertContains(response, "ada@example.com")
        self.assertContains(response, "root@example.com")

    def test_changelist_search_works_on_email(self):
        url = reverse("admin:accounts_baseuser_changelist")
        response = self.client.get(url, {"q": "ada@"})
        found = [user.email for user in response.context["cl"].result_list]
        self.assertEqual(found, ["ada@example.com"])

    def test_change_page_loads(self):
        url = reverse("admin:accounts_baseuser_change", args=[self.ada.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ada@example.com")

    def test_add_form_creates_a_user(self):
        url = reverse("admin:accounts_baseuser_add")
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post(
            url,
            {
                "email": "New@Example.com",
                "username": "new",
                "usable_password": "true",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 302)
        created = User.objects.get(username="new")
        self.assertEqual(created.email, "new@example.com")
        self.assertTrue(created.check_password(PASSWORD))

    def test_add_form_shows_an_error_for_a_duplicate_email_in_another_case(self):
        response = self.client.post(
            reverse("admin:accounts_baseuser_add"),
            {
                "email": "ADA@example.com",
                "username": "other",
                "usable_password": "true",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that email already exists.")
        self.assertEqual(User.objects.filter(username="other").count(), 0)

    def test_change_form_saves_edits(self):
        url = reverse("admin:accounts_baseuser_change", args=[self.ada.pk])
        joined = self.ada.date_joined
        response = self.client.post(
            url,
            {
                "username": "ada",
                "email": "Ada.New@Example.com",
                "first_name": "Ada",
                "last_name": "Lovelace",
                "is_active": "on",
                "date_joined_0": joined.strftime("%Y-%m-%d"),
                "date_joined_1": joined.strftime("%H:%M:%S"),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.ada.refresh_from_db()
        self.assertEqual(self.ada.email, "ada.new@example.com")
        self.assertEqual(self.ada.first_name, "Ada")


class AdminAccessTests(AccountsTestCase):
    def test_anonymous_users_are_sent_to_the_admin_login(self):
        response = self.client.get(reverse("admin:accounts_baseuser_changelist"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_non_staff_users_cannot_use_the_admin(self):
        self.client.force_login(self.make_user())
        response = self.client.get(reverse("admin:accounts_baseuser_changelist"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])

    def test_staff_without_permissions_get_403_on_the_user_list(self):
        staff = self.make_user(email="staff@example.com", username="staff", is_staff=True)
        self.client.force_login(staff)
        response = self.client.get(reverse("admin:accounts_baseuser_changelist"))
        self.assertEqual(response.status_code, 403)
