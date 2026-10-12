from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path


def home(request):
    return render(request, "landing.html")


def auth_screen(request, screen):
    """Thin HTML shell that mounts the Vite/React auth bundle."""
    return render(request, "auth.html", {"screen": screen})


urlpatterns = [
    path("", home, name="home"),
    path("accounts/signup/", auth_screen, {"screen": "signup"}, name="signup"),
    path("accounts/signin/", auth_screen, {"screen": "signin"}, name="signin"),
    path("accounts/logout/", auth_screen, {"screen": "logout"}, name="logout"),
    path("api/auth/", include("accounts.api_urls")),
    path("admin/", admin.site.urls),
]