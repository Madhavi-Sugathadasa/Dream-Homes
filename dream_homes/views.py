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

    
# logout view
def logout_view(request):
    logout(request)
    return render(request, "users/login.html", {"message": None})


# forgot password, recover through an email
def forgot_password(request):
    if request.method == 'POST':
        return password_reset(request, from_email=request.POST.get('email'))
    else:
        return render(request, 'users/forgot_password.html')

    
    
#index page
@login_required(login_url='login')
def index(request):
    try:
        buy_ad_items = None
        rent_ad_items = None
        context = {}
        main_search_type = ""
        
        if request.method == "POST":
            
            search_type = request.POST["search_type"]
            main_search_type = search_type
            context.update(search_type = search_type )
            
            if search_type == 'buy':
                property_type = request.POST["property_type"]
                # filter property type
                if property_type and property_type != "ALL":
                    context.update(property_type_val = property_type )
                    buy_ad_items = Buy_Ad_Item.objects.filter(active = True, payment = True, property_type__code = property_type)
                    
                else:
                    buy_ad_items = Buy_Ad_Item.objects.filter(active = True, payment = True)
                
                # filter by location and if include surrounding surburbs checked - search surburbs within 25 kms of location
                # for this functionality had to use sql math functions extention
                location_str = request.POST["location"]
                surrounding = request.POST.get("surrounding")
                if surrounding:
                    context.update(surrounding = True )
                if location_str:
                    location_data  = location_str.split(", ")
                    if len(location_data) == 3:
                        location= Location.objects.get(Q(postcode=location_data[2]) & Q(suburb=location_data[0]) & Q(state=location_data[1]))
                        if location:
                            context.update(location_val = location )

                            if surrounding:
                                conn = sqlite3.connect(os.path.join(conf_settings.BASE_DIR, 'db.sqlite3'))
                                conn.enable_load_extension(True)
                                conn.load_extension("./math")
                                c = conn.cursor()
                                c.execute('Select id From dream_homes_location Where acos(sin(radians(?))*sin(radians(lat)) + cos(radians(?))*cos(radians(lat))*cos(radians(lon)- radians(?))) * 6371 < ?', (location.lat, location.lat, location.lon, 25))

                                rows = c.fetchall()
                                surrounding_subs = [i[0] for i in rows]
                                conn.enable_load_extension(False)
                                conn.close()
                                buy_ad_items = buy_ad_items.filter(location__id__in = surrounding_subs)
                            else:
                                buy_ad_items = buy_ad_items.filter(location = location)
                
                # filter by price range
                price_range = request.POST["price_range"]
                
                if price_range:
                    context.update(price_range_val = float(price_range))
                    
                    if float(price_range) == 10000000:
                        buy_ad_items = buy_ad_items.filter(to_price__gte =float(price_range))
                    elif float(price_range) < 10000000 and float(price_range) > 0:
                        buy_ad_items = buy_ad_items.filter(from_price__lte =float(price_range))
                    #else all items - no price range filter
                
                # filter by bedrooms    
                bedrooms = request.POST["bedrooms"]
                if bedrooms and bedrooms != "ANY":
                    buy_ad_items = buy_ad_items.filter(bedrooms__gte = int(bedrooms))
                    context.update(bedrooms_val = int(bedrooms) )
                
                # filter by bathrooms    
                bathrooms = request.POST["bathrooms"]
                if bathrooms and bathrooms != "ANY":
                    buy_ad_items = buy_ad_items.filter(bathrooms__gte = int(bathrooms))
                    context.update(bathrooms_val = int(bathrooms) )
                
                # filter by parking    
                parking = request.POST["parking"]
                if parking and parking != "ANY":
                    buy_ad_items = buy_ad_items.filter(parking__gte = int(parking))
                    context.update(parking_val = int(parking) )
                    
                # sort by most recent(MR) or Location_A_Z(AZ) or Location_Z_A (ZA) or Price (High- Low) or Price (Low - High)
                sort = request.POST["sort"]
                if sort:
                    context.update(sort_val = sort )
                    if sort == "MR":
                        buy_ad_items = buy_ad_items.order_by('-priority').order_by('-date_time')
                    if sort == "AZ":
                        buy_ad_items = buy_ad_items.order_by('-priority').order_by('location__suburb')
                    if sort == "ZA":
                        buy_ad_items = buy_ad_items.order_by('-priority').order_by('-location__suburb')
                    if sort == "HL":
                        buy_ad_items = buy_ad_items.order_by('-priority').order_by('-to_price')
                    if sort == "LH":
                        buy_ad_items = buy_ad_items.order_by('-priority').order_by('to_price')
                
                
            elif search_type == 'rent':
                rent_property_type = request.POST["rent_property_type"]
                # filter by property type
                if rent_property_type and rent_property_type != "ALL":
                    rent_ad_items = Rent_Ad_Item.objects.filter(active = True, payment = True, property_type__code = rent_property_type)
                    context.update(rent_property_type_val = rent_property_type )
                else:
                    rent_ad_items = Rent_Ad_Item.objects.filter(active = True, payment = True)

                # filter by location and if include surrounding surburbs checked - search surburbs within 25 kms of location
                # for this functionality had to use sql math functions extention
                location_str = request.POST["rent_location"]
                surrounding = request.POST.get("rent_surrounding")
                if surrounding:
                    context.update(rent_surrounding = True )
                if location_str:
                    location_data  = location_str.split(", ")
                    if len(location_data) == 3:
                        location= Location.objects.get(Q(postcode=location_data[2]) & Q(suburb=location_data[0]) & Q(state=location_data[1]))
                        if location:
                            context.update(rent_location = location )

                            if surrounding:
                                conn = sqlite3.connect(os.path.join(conf_settings.BASE_DIR, 'db.sqlite3'))
                                conn.enable_load_extension(True)
                                conn.load_extension("./math")
                                c = conn.cursor()
                                c.execute('Select id From dream_homes_location Where acos(sin(radians(?))*sin(radians(lat)) + cos(radians(?))*cos(radians(lat))*cos(radians(lon)- radians(?))) * 6371 < ?', (location.lat, location.lat, location.lon, 25))

                                rows = c.fetchall()
                                surrounding_subs = [i[0] for i in rows]
                                conn.enable_load_extension(False)
                                conn.close()
                                rent_ad_items = rent_ad_items.filter(location__id__in = surrounding_subs)
                            else:
                                rent_ad_items = rent_ad_items.filter(location = location)

                # filter by price range
                price_range = request.POST["rent_price_range"]
                if price_range:
                    context.update(rent_price_range = float(price_range) )
                    if float(price_range) == 1500:
                        rent_ad_items = rent_ad_items.filter(weekly_price__gte =float(price_range))
                    elif float(price_range) < 1500 and float(price_range) > 0:
                        rent_ad_items = rent_ad_items.filter( weekly_price__lte =float(price_range))
                     #else all items - no price range filter


                # filter by bedrooms    
                bedrooms = request.POST["rent_bedrooms"]
                if bedrooms and bedrooms != "ANY":
                    rent_ad_items = rent_ad_items.filter(bedrooms__gte = int(bedrooms))
                    context.update(rent_bedrooms_val = int(bedrooms))

                # filter by bathrooms    
                bathrooms = request.POST["rent_bathrooms"]
                if bathrooms and bathrooms != "ANY":
                    rent_ad_items = rent_ad_items.filter(bathrooms__gte = int(bathrooms))
                    context.update(rent_bathrooms_val = int(bathrooms))

                # filter by parking    
                parking = request.POST["rent_parking"]
                if parking and parking != "ANY":
                    rent_ad_items = rent_ad_items.filter(parking__gte = int(parking))
                    context.update(rent_parking_val = int(parking))
                    
                # sort by most recent(MR) or Location_A_Z(AZ) or Location_Z_A (ZA) or Most Expensive(HL) or Cheapest(LH)
                sort = request.POST["sort"]
                if sort:
                    context.update(sort_val = sort )
                    if sort == "MR":
                        rent_ad_items = rent_ad_items.order_by('-priority').order_by('-date_time')
                    if sort == "AZ":
                        rent_ad_items = rent_ad_items.order_by('-priority').order_by('location__suburb')
                    if sort == "ZA":
                        rent_ad_items = rent_ad_items.order_by('-priority').order_by('-location__suburb')
                    if sort == "HL":
                        rent_ad_items = rent_ad_items.order_by('-priority').order_by('-weekly_price')
                    if sort == "LH":
                        rent_ad_items = rent_ad_items.order_by('-priority').order_by('weekly_price')
        else:
            
            context.update(search_type = "get" )
            main_search_type = "get" 
        
        page_obj = None
        dict_photo_items ={}

       
        if main_search_type and main_search_type == "buy":
            # pagination
            paginator = Paginator(buy_ad_items, conf_settings.NO_OF_ADS_PER_PAGE)
            page_number = request.POST.get('page')
            page_obj = paginator.get_page(page_number)
        
            for buy_ad_item in page_obj:
                # laod photos for each ad item
                photo_items = Buy_Item_Picture.objects.filter(ad_item =buy_ad_item)
                if photo_items:
                    dict_photo_items[buy_ad_item.id] = photo_items 
                
        elif main_search_type and main_search_type == "rent":
            # pagination
            paginator = Paginator(rent_ad_items, conf_settings.NO_OF_ADS_PER_PAGE)
            page_number = request.POST.get('page')
            page_obj = paginator.get_page(page_number)
        
            for rent_ad_item in page_obj:
                # laod photos for each ad item
                photo_items = Rent_Item_Picture.objects.filter(ad_item =rent_ad_item)
                if photo_items:
                    dict_photo_items[rent_ad_item.id] = photo_items

                    
    except Buy_Ad_Item.DoesNotExist:
        return render(request, "error.html", {"message": "Ad items does not exist."})
    except Rent_Ad_Item.DoesNotExist:
        return render(request, "error.html", {"message": "Ad items does not exist."})
    except Buy_Item_Picture.DoesNotExist:
        return render(request, "error.html", {"message": "Ad items does not exist."})
    except Rent_Item_Picture.DoesNotExist:
        return render(request, "error.html", {"message": "Ad items does not exist."})
    
    # load all below details to populate filter section
    property_types = Property_Type.objects.all().order_by('name')
    bedrooms = Bedroom.objects.all().order_by('code')
    bathrooms = Bathroom.objects.all().order_by('code')
    parkings = Parking.objects.all().order_by('code')
    
    context.update({'page_obj': page_obj, "photo_items":dict_photo_items, "property_types":property_types, "bedrooms":bedrooms, "bathrooms":bathrooms, "parkings":parkings})
    
    return render(request, "index.html", context)


