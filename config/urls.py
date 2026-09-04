from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

from accounts import views as account_views


def home(request):
    return render(request, "landing.html")


urlpatterns = [
    path("", home, name="home"),
    path("accounts/", include(([
        path("signup/", account_views.signup, name="signup"),
        path("signin/", account_views.signin, name="signin"),
    ], "accounts"))),
    path("admin/", admin.site.urls),
]
