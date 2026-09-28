from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

User = get_user_model()

VALID_PASSWORD = "Str0ngPass!2345"


class SignupApiTests(TestCase):
    url = "/api/auth/signup/"

    def payload(self, **overrides):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": VALID_PASSWORD,
            "confirm_password": VALID_PASSWORD,
        }
        data.update(overrides)
        return data

    def test_creates_user_and_returns_token(self):
        response = self.client.post(self.url, self.payload(), content_type="application/json")

        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["username"], "newuser")
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertEqual(Token.objects.count(), 1)

    def test_password_is_hashed_not_stored_plaintext(self):
        self.client.post(self.url, self.payload(), content_type="application/json")

        user = User.objects.get(username="newuser")
        self.assertNotEqual(user.password, VALID_PASSWORD)
        self.assertTrue(user.check_password(VALID_PASSWORD))

    def test_rejects_duplicate_username(self):
        User.objects.create_user("taken", "t@example.com", VALID_PASSWORD)

        response = self.client.post(
            self.url, self.payload(username="taken"), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)

    def test_rejects_mismatched_passwords(self):
        response = self.client.post(
            self.url,
            self.payload(confirm_password="Different!2345"),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("confirm_password", response.data)

    def test_rejects_weak_password(self):
        response = self.client.post(
            self.url, self.payload(password="123", confirm_password="123"), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)

    def test_rejects_invalid_email(self):
        response = self.client.post(
            self.url, self.payload(email="not-an-email"), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_uses_same_token_across_requests(self):
        self.client.post(self.url, self.payload(), content_type="application/json")
        self.client.post(self.url, self.payload(username="other", email="o@example.com"), content_type="application/json")

        self.assertEqual(Token.objects.count(), 2)


class SigninApiTests(TestCase):
    url = "/api/auth/signin/"

    def setUp(self):
        self.user = User.objects.create_user("member", "m@example.com", VALID_PASSWORD)

    def test_returns_token_for_valid_credentials(self):
        response = self.client.post(
            self.url,
            {"username": "member", "password": VALID_PASSWORD},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["token"], Token.objects.get(user=self.user).key)

    def test_rejects_wrong_password(self):
        response = self.client.post(
            self.url, {"username": "member", "password": "nope"}, content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.data)

    def test_rejects_unknown_user(self):
        response = self.client.post(
            self.url,
            {"username": "ghost", "password": VALID_PASSWORD},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_inactive_user_cannot_sign_in(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.url,
            {"username": "member", "password": VALID_PASSWORD},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)


class MeApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("member", "m@example.com", VALID_PASSWORD)
        self.token = Token.objects.create(user=self.user)

    def test_requires_authentication(self):
        response = self.client.get("/api/auth/me/")

        self.assertEqual(response.status_code, 401)

    def test_returns_current_user_for_valid_token(self):
        response = self.client.get(
            "/api/auth/me/", HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "member")

    def test_rejects_bogus_token(self):
        response = self.client.get("/api/auth/me/", HTTP_AUTHORIZATION="Token deadbeef")

        self.assertEqual(response.status_code, 401)


class LogoutApiTests(TestCase):
    def test_logout_invalidates_token(self):
        user = User.objects.create_user("member", "m@example.com", VALID_PASSWORD)
        token = Token.objects.create(user=user)

        response = self.client.post(
            "/api/auth/logout/", HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Token.objects.filter(user=user).exists())

    def test_logout_is_safe_without_a_token(self):
        response = self.client.post("/api/auth/logout/")

        self.assertEqual(response.status_code, 204)


class PageTests(TestCase):
    """The auth routes must keep serving the React shell for each screen."""

    def test_landing_page_renders(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_signin_screen_shell(self):
        response = self.client.get(reverse("signin"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-screen="signin"')

    def test_signup_screen_shell(self):
        response = self.client.get(reverse("signup"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-screen="signup"')

    def test_logout_screen_shell(self):
        response = self.client.get(reverse("logout"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-screen="logout"')

    def test_signin_shell_links_bundle_and_stylesheet(self):
        response = self.client.get(reverse("signin"))

        self.assertContains(response, "auth/auth.js")
        self.assertContains(response, "auth/auth.css")
