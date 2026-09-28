from django.urls import path
from rest_framework.authtoken import views as drf_authtoken_views

from . import api

urlpatterns = [
    path("signup/", api.SignupView.as_view(), name="api-signup"),
    path("signin/", api.SigninView.as_view(), name="api-signin"),
    path("logout/", api.LogoutView.as_view(), name="api-logout"),
    path("me/", api.MeView.as_view(), name="api-me"),
    path(
        "token/",
        drf_authtoken_views.obtain_auth_token,
        name="api-token",
    ),
]
