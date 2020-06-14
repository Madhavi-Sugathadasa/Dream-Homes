from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Location, Property_Type, Bedroom, Bathroom, Parking, Buy_Item_Ad_Type, Buy_Ad_Item, Buy_Item_Picture, Buy_Item_Inspection, Rent_Ad_Item, Rent_Item_Picture, Rent_Item_Inspection
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings as conf_settings
import os
import sqlite3
from datetime import datetime, date, time
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import stripe
from django.conf import settings
from django.db import connection

stripe.api_key = getattr(settings, "STRIPE_SECRET_API_KEY", None)
# Create your views here.

#login page
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        if not username:
            return render(request, "users/login.html", {"message": "Must provide username."})
        if not password:
            return render(request, "users/login.html", {"message": "Must provide password."})
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "users/login.html", {"message": "Invalid credentials."})
    else:
        request.session.clear()
        return render(request, "users/login.html", {"message": None})

#register a new user   
def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]

        if not username:
            return render(request, "users/register.html", {"message": "Must provide username."})
        if not password:
            return render(request, "users/register.html", {"message": "Must provide password."})
        if password != confirm_password:
            return render(request, "users/register.html", {"message": "Passwords didn't match."})
        if not first_name:
            return render(request, "users/register.html", {"message": "Must provide first name."})
        if not last_name:
            return render(request, "users/register.html", {"message": "Must provide last name."})
        if not email:
            return render(request, "users/register.html", {"message": "Must provide email."})

        try:
            User.objects.create_user(username=username, password=password,  first_name=first_name, last_name=last_name, email=email)
        except IntegrityError:
            return render(request, "users/register.html", {"message": "User already exists."})
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "users/login.html", {"message": "Invalid credentials."})
    else:
        return render(request, "users/register.html", {"message":None})
