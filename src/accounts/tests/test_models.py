from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase

from .test_base import PASSWORD, User


class BaseUserModelTests(TestCase):
    def test_email_is_the_username_field(self):
        self.assertEqual(User.USERNAME_FIELD, "email")
        self.assertEqual(User.REQUIRED_FIELDS, ["username"])

    def test_username_is_kept_and_required(self):
        user = User.objects.create_user(
            username="ada", email="ada@example.com", password=PASSWORD
        )
        self.assertEqual(user.username, "ada")
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", email="x@example.com", password="p")

    def test_str_and_get_username_are_the_email(self):
        user = User.objects.create_user(
            username="ada", email="ada@example.com", password=PASSWORD
        )
        self.assertEqual(str(user), "ada@example.com")
        self.assertEqual(user.get_username(), "ada@example.com")

    def test_email_is_stripped_and_lowercased_on_create(self):
        user = User.objects.create_user(
            username="ada", email="  Ada@Example.COM ", password=PASSWORD
        )
        self.assertEqual(user.email, "ada@example.com")

    def test_email_is_lowercased_on_every_save(self):
        user = User.objects.create_user(
            username="ada", email="ada@example.com", password=PASSWORD
        )
        user.email = "ADA@Example.com"
        user.save()
        user.refresh_from_db()
        self.assertEqual(user.email, "ada@example.com")

    def test_save_with_update_fields_still_works(self):
        user = User.objects.create_user(
            username="ada", email="ada@example.com", password=PASSWORD
        )
        user.first_name = "Ada"
        user.save(update_fields=["first_name"])
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Ada")

    def test_email_is_required(self):
        for email in (None, "", "   "):
            with self.subTest(email=email), self.assertRaises(ValueError):
                User.objects.create_user(username="ada", email=email, password=PASSWORD)
        self.assertEqual(User.objects.count(), 0)

    def test_email_must_be_unique_regardless_of_case(self):
        User.objects.create_user(username="a", email="a@example.com", password=PASSWORD)
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(
                username="b", email="A@EXAMPLE.com", password=PASSWORD
            )

    def test_username_must_still_be_unique(self):
        User.objects.create_user(username="a", email="a@example.com", password=PASSWORD)
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(
                username="a", email="b@example.com", password=PASSWORD
            )

    def test_full_clean_reports_duplicate_email_case_insensitively(self):
        User.objects.create_user(username="a", email="a@example.com", password=PASSWORD)
        duplicate = User(username="b", email="A@Example.com")
        with self.assertRaises(ValidationError) as ctx:
            duplicate.full_clean(exclude=["password"])
        self.assertIn("email", ctx.exception.message_dict)
        self.assertEqual(
            ctx.exception.message_dict["email"],
            ["A user with that email already exists."],
        )

    def test_full_clean_rejects_a_malformed_email(self):
        user = User(username="a", email="not-an-email")
        with self.assertRaises(ValidationError) as ctx:
            user.full_clean(exclude=["password"])
        self.assertIn("email", ctx.exception.message_dict)

    def test_get_by_natural_key_looks_up_by_email(self):
        user = User.objects.create_user(
            username="ada", email="ada@example.com", password=PASSWORD
        )
        self.assertEqual(User.objects.get_by_natural_key("ada@example.com"), user)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get_by_natural_key("ada")

    def test_password_is_hashed(self):
        user = User.objects.create_user(
            username="ada", email="ada@example.com", password=PASSWORD
        )
        self.assertNotEqual(user.password, PASSWORD)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertFalse(user.check_password("wrong"))

    def test_new_users_are_active_and_not_staff(self):
        user = User.objects.create_user(
            username="ada", email="ada@example.com", password=PASSWORD
        )
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff or user.is_superuser)


class SuperuserTests(TestCase):
    def test_create_superuser_sets_flags(self):
        admin = User.objects.create_superuser(
            username="root", email="Root@Example.com", password=PASSWORD
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.email, "root@example.com")

    def test_create_superuser_refuses_non_staff_flags(self):
        for flag in ("is_staff", "is_superuser"):
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                User.objects.create_superuser(
                    username="root",
                    email="root@example.com",
                    password=PASSWORD,
                    **{flag: False},
                )

    def test_createsuperuser_command_asks_for_email_and_username(self):
        call_command(
            "createsuperuser",
            interactive=False,
            email="Boss@Example.com",
            username="boss",
            stdout=StringIO(),
            stderr=StringIO(),
            verbosity=0,
        )
        boss = User.objects.get(email="boss@example.com")
        self.assertEqual(boss.username, "boss")
        self.assertTrue(boss.is_superuser)


class MigrationTests(TestCase):
    def test_no_model_changes_are_missing_a_migration(self):
        out = StringIO()
        try:
            call_command(
                "makemigrations", "--check", "--dry-run", stdout=out, stderr=out
            )
        except SystemExit:
            self.fail(f"Model changes without a migration:\n{out.getvalue()}")
