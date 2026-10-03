from django.test import RequestFactory, TestCase

from accounts.forms import (
    BaseUserChangeForm,
    BaseUserCreationForm,
    BaseUserLoginForm,
)

from .test_base import PASSWORD, User


def login_form(email, password):
    request = RequestFactory().post("/accounts/login/")
    return BaseUserLoginForm(request, data={"username": email, "password": password})


class LoginFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="ada", email="ada@example.com", password=PASSWORD
        )

    def test_valid_credentials(self):
        form = login_form("ada@example.com", PASSWORD)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.get_user(), self.user)

    def test_email_is_case_and_whitespace_insensitive(self):
        form = login_form("  ADA@Example.com ", PASSWORD)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.get_user(), self.user)

    def test_username_is_not_accepted_as_login(self):
        form = login_form("ada", PASSWORD)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_both_fields_are_required(self):
        form = BaseUserLoginForm(RequestFactory().post("/"), data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(set(form.errors), {"username", "password"})

    def test_username_field_is_an_email_input_labelled_email(self):
        field = BaseUserLoginForm().fields["username"]
        self.assertEqual(field.label, "Email")
        self.assertEqual(field.widget.input_type, "email")

    def test_wrong_password_and_unknown_email_give_the_same_error(self):
        wrong_password = login_form("ada@example.com", "nope")
        unknown_email = login_form("nobody@example.com", PASSWORD)
        self.assertFalse(wrong_password.is_valid())
        self.assertFalse(unknown_email.is_valid())
        self.assertEqual(wrong_password.non_field_errors(), unknown_email.non_field_errors())

    def test_deactivated_account_with_correct_password_is_flagged(self):
        User.objects.filter(pk=self.user.pk).update(is_active=False)
        form = login_form("ada@example.com", PASSWORD)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors().as_data()[0].code, "inactive")

    def test_deactivated_account_with_wrong_password_stays_generic(self):
        User.objects.filter(pk=self.user.pk).update(is_active=False)
        form = login_form("ada@example.com", "nope")
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors().as_data()[0].code, "invalid_login")


class CreationFormTests(TestCase):
    def data(self, **overrides):
        data = {
            "email": "new@example.com",
            "username": "new",
            "usable_password": "true",
            "password1": PASSWORD,
            "password2": PASSWORD,
        }
        data.update(overrides)
        return data

    def test_creates_a_user_with_a_lowercase_email(self):
        form = BaseUserCreationForm(self.data(email="New@Example.COM"))
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.email, "new@example.com")
        self.assertTrue(user.check_password(PASSWORD))

    def test_rejects_a_duplicate_email_in_any_case(self):
        User.objects.create_user(username="a", email="new@example.com", password=PASSWORD)
        form = BaseUserCreationForm(self.data(email="NEW@example.com", username="b"))
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_rejects_a_duplicate_username(self):
        User.objects.create_user(username="new", email="a@example.com", password=PASSWORD)
        form = BaseUserCreationForm(self.data())
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_rejects_mismatched_passwords(self):
        form = BaseUserCreationForm(self.data(password2="different-pass-9"))
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_rejects_a_weak_password(self):
        form = BaseUserCreationForm(self.data(password1="12345678", password2="12345678"))
        self.assertFalse(form.is_valid())

    def test_requires_a_valid_email(self):
        form = BaseUserCreationForm(self.data(email="nope"))
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class ChangeFormTests(TestCase):
    def test_is_bound_to_the_custom_user_model(self):
        self.assertIs(BaseUserChangeForm._meta.model, User)
        self.assertIn("email", BaseUserChangeForm().fields)

    def test_cannot_change_email_to_an_existing_one(self):
        User.objects.create_user(username="a", email="a@example.com", password=PASSWORD)
        other = User.objects.create_user(username="b", email="b@example.com", password=PASSWORD)
        form = BaseUserChangeForm(
            {"email": "A@example.com", "username": "b", "date_joined": other.date_joined},
            instance=other,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
