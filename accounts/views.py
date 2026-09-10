
from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect


class SignupForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)


class SigninForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    
    
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            if User.objects.filter(username=username).exists():
                form.add_error("username", "Username already taken.")
            else:
                password = form.cleaned_data["password"]
                if password != form.cleaned_data["confirm_password"]:
                    form.add_error("confirm_password", "Passwords do not match.")
                else:
                    try:
                        validate_password(password)
                    except ValidationError as e:
                        form.add_error("password", e)
                    else:
                        user = User.objects.create_user(
                            username, form.cleaned_data["email"], password
                        )
                        login(request, user)
                        return redirect("home")
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form, "errors": form.errors})


def signin(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username", ""),
            password=request.POST.get("password", ""),
        )
        if user is not None:
            login(request, user)
            return redirect("home")
        return render(request, "signin.html", {"error": "Invalid username or password."})
    return render(request, "signin.html")
