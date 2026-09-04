from django.shortcuts import render, redirect
from . import json_db

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        json_db.create_user(username, email, password)
        return redirect("signin")
        
    return render(request, "signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = json_db.authenticate_user(username, password)
        if user:
            request.session["user_id"] = user["username"]
            return redirect("/")
        else:
            return render(request, "signin.html", {"error": "نام کاربری یا رمز عبور اشتباه است."})
        
    return render(request, "signin.html")