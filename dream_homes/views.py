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
    