from django.contrib.auth import views as auth_views

from .forms import BaseUserLoginForm


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = BaseUserLoginForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    next_page = "accounts:login"
