from django.test import TestCase, override_settings
from django.urls import path


def forbidden(request):
    from django.core.exceptions import PermissionDenied

    raise PermissionDenied


urlpatterns = [path("forbidden/", forbidden)] + __import__(
    "django_starter.urls", fromlist=["urlpatterns"]
).urlpatterns


@override_settings(SECURE_SSL_REDIRECT=False, DEBUG=False, ROOT_URLCONF=__name__)
class ErrorPageTests(TestCase):
    def test_404_uses_the_project_template(self):
        response = self.client.get("/does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(response, "Page not found", status_code=404)

    def test_403_uses_the_project_template(self):
        response = self.client.get("/forbidden/")
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")

    def test_500_template_renders(self):
        from django.template.loader import render_to_string

        html = render_to_string("500.html")
        self.assertIn("Something went wrong", html)
        self.assertIn("500", html)
