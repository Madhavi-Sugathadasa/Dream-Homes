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


# ajax call for location autocomplete
def autocomplete_location(request):
    if request.is_ajax():
        location = request.GET.get('search', None)
        queryset = Location.objects.filter(Q(postcode__contains=location) | Q(suburb__contains=location) | Q(state__contains=location))
        list = []        
        for i in queryset:
            list.append(i.suburb+", " + i.state + ", " + i.postcode)
        data = {
            'list': list,
        }
        return JsonResponse(data)
    
# more details of a selected Ad
@login_required(login_url='login')
def ad_more_details(request, ad_id, ad_type):
    
    try:
        if ad_type and ad_type == 'rent':
            item = Rent_Ad_Item.objects.get(pk=ad_id)
            photo_items = Rent_Item_Picture.objects.filter(ad_item =item)
            inspections = Rent_Item_Inspection.objects.filter(ad_item =item).order_by('from_time').order_by('date')
        else:
            item = Buy_Ad_Item.objects.get(pk=ad_id)
            photo_items = Buy_Item_Picture.objects.filter(ad_item =item)
            inspections = Buy_Item_Inspection.objects.filter(ad_item =item).order_by('from_time').order_by('date')
    except Buy_Ad_Item.DoesNotExist:
        return render(request, "error.html", {"message": "item does not exist."})
    except Rent_Ad_Item.DoesNotExist:
        return render(request, "error.html", {"message": "item does not exist."})
    except Buy_Item_Picture.DoesNotExist:
        return render(request, "error.html", {"message": "photo items does not exist."})
    except Rent_Item_Picture.DoesNotExist:
        return render(request, "error.html", {"message": "photo items does not exist."})
    except Buy_Item_Inspection.DoesNotExist:
        return render(request, "error.html", {"message": "inspection items does not exist."})
    except Rent_Item_Inspection.DoesNotExist:
        return render(request, "error.html", {"message": "inspection items does not exist."})
    context = {
      "item": item,"photo_items":photo_items, "inspections":inspections, "ad_type":ad_type,"GOOGLE_MAP_KEY":conf_settings.GOOGLE_MAP_KEY,
    }
    return render(request, "item.html", context)


# post a new Ad    
@login_required(login_url='login')
def post_ad(request):
    if request.method == "POST":
        ad_id = None
        property_ad_type = None
        payment_pkg_type = None
        
        try:
            # action type - payment or save without payment
            action = request.POST["action"]
            ad_property_type = request.POST["ad_property_type"]
            if ad_property_type == 'rent':
                
                ad_item = Rent_Ad_Item()
                ad_item.user = request.user
                weekly_price = request.POST["weekly_price"]
                ad_item.weekly_price = float(weekly_price)
                
                title = request.POST["rent_title"]
                ad_item.title = title
                
                desc = request.POST["rent_description"]
                ad_item.desc = desc
                
                property_type = request.POST["rent_property_type"]
                ad_item.property_type = Property_Type.objects.get(code=property_type)
                
                address_line = request.POST["rent_address_line"]
                ad_item.address_line = address_line
                
                location_str = request.POST["rent_location"]
                if location_str:
                    location_data  = location_str.split(", ")
                    if len(location_data) == 3:
                        location = Location.objects.get(Q(postcode=location_data[2]) & Q(suburb=location_data[0]) & Q(state=location_data[1]))
                        if location:
                            ad_item.location = location
                        else:
                            return render(request, "error.html", {"message": "Invalid item location."})
                    else:
                        return render(request, "error.html", {"message": "Invalid item location."})
                else:
                    return render(request, "error.html", {"message": "Invalid item location."})
                
                bedrooms = request.POST["rent_bedrooms"]
                ad_item.bedrooms = int(bedrooms)
                
                bathrooms = request.POST["rent_bathrooms"]
                ad_item.bathrooms = int(bathrooms)
                
                parking = request.POST["rent_parking"]
                ad_item.parking = int(parking)
                
                garages = request.POST["rent_garages"]
                ad_item.garages = int(garages)
                
                contact_name = request.POST["rent_contact_name"]
                ad_item.contact_name = contact_name

                contact_email = request.POST["rent_contact_email"]
                ad_item.email = contact_email

                mobile = request.POST["rent_mobile"]
                ad_item.mobile = mobile
                
                
                ad_item.date_time = datetime.now()
                ad_item.active = True
                ad_item.save()
                
                
                floorplan = request.FILES.get('rent_floorplan')
                if floorplan:
                    ad_item.floorplan = floorplan
                ad_item.save()
                
                for i in range(1,7):
                    img = request.FILES.get('rent_img_' + str(i))
                    if img:
                        picture = Rent_Item_Picture()
                        picture.ad_item = ad_item
                        picture.image = img
                        picture.save()
                    
                for i in range(1,5):
                    ins_date = request.POST.get('rent_ins_date_' + str(i))
                    ins_from_time = request.POST.get('rent_ins_from_time_' + str(i))
                    ins_to_time = request.POST.get('rent_ins_to_time_' + str(i))
                    if ins_date:
                        insp = Rent_Item_Inspection()
                        insp.ad_item = ad_item
                        insp.ad_item = ad_item
                        insp.date = datetime.strptime(ins_date, '%Y-%m-%d')
                        insp.from_time = datetime.strptime(ins_from_time, '%H:%M')
                        insp.to_time = datetime.strptime(ins_to_time, '%H:%M')
                        insp.save()
                
                payment_pkg = request.POST["rent_payment_pkg"]
                ad_id = ad_item.id
                property_ad_type = ad_property_type
                payment_pkg_type = payment_pkg
                
                
            else:
                
                ad_item = Buy_Ad_Item()
                ad_item.user = request.user
                from_price = request.POST["from_price"]
                if from_price:
                    ad_item.from_price = float(from_price)
                else:
                    ad_item.from_price = 0.0
                to_price = request.POST["to_price"]
                if to_price:
                    ad_item.to_price = float(to_price)
                else:
                    ad_item.to_price = 0.0
                ad_type = request.POST["ad_type"]
                ad_item.ad_type = Buy_Item_Ad_Type.objects.get(pk=ad_type)
                
                title = request.POST["title"]
                ad_item.title = title
                
                desc = request.POST["description"]
                ad_item.desc = desc
                
                property_type = request.POST["property_type"]
                ad_item.property_type = Property_Type.objects.get(code=property_type)
                
                action_date = request.POST["action_date"]
                if action_date:
                    ad_item.auction_date = datetime.strptime(action_date, '%Y-%m-%dT%H:%M')
                
                address_line = request.POST["address_line"]
                ad_item.address_line = address_line
                
                
                location_str = request.POST["location"]
                if location_str:
                    location_data  = location_str.split(", ")
                    if len(location_data) == 3:
                        location = Location.objects.get(Q(postcode=location_data[2]) & Q(suburb=location_data[0]) & Q(state=location_data[1]))
                        if location:
                            ad_item.location = location
                        else:
                            return render(request, "error.html", {"message": "Invalid item location."})
                    else:
                        return render(request, "error.html", {"message": "Invalid item location."})
                else:
                    return render(request, "error.html", {"message": "Invalid item location."})
                
                bedrooms = request.POST["bedrooms"]
                ad_item.bedrooms = int(bedrooms)
                
                bathrooms = request.POST["bathrooms"]
                ad_item.bathrooms = int(bathrooms)
                
                parking = request.POST["parking"]
                ad_item.parking = int(parking)
                
                garages = request.POST["garages"]
                ad_item.garages = int(garages)
                
                land_area = request.POST["land_area"]
                ad_item.land_area = land_area
                
                contact_name = request.POST["contact_name"]
                ad_item.contact_name = contact_name

                contact_email = request.POST["contact_email"]
                ad_item.email = contact_email

                mobile = request.POST["mobile"]
                ad_item.mobile = mobile
            
                ad_item.date_time = datetime.now()
                ad_item.active = True
                ad_item.save()
                
                floorplan = request.FILES.get('floorplan')
                if floorplan:
                    ad_item.floorplan = floorplan
                ad_item.save()
                
                for i in range(1,7):
                    img = request.FILES.get('img_' + str(i))
                    if img:
                        picture = Buy_Item_Picture()
                        picture.ad_item = ad_item
                        picture.image = img
                        picture.save()
                    
                for i in range(1,5):
                    ins_date = request.POST.get('ins_date_' + str(i))
                    ins_from_time = request.POST.get('ins_from_time_' + str(i))
                    ins_to_time = request.POST.get('ins_to_time_' + str(i))
                    
                    if ins_date:
                        insp = Buy_Item_Inspection()
                        insp.ad_item = ad_item
                        insp.date = datetime.strptime(ins_date, '%Y-%m-%d')
                        insp.from_time = datetime.strptime(ins_from_time, '%H:%M')
                        insp.to_time = datetime.strptime(ins_to_time, '%H:%M')
                        insp.save()
                
                payment_pkg = request.POST["payment_pkg"]
                ad_id = ad_item.id
                property_ad_type = ad_property_type
                payment_pkg_type = payment_pkg
            
            if action == 'payment':    
                return HttpResponseRedirect(reverse("payment",args=(property_ad_type, ad_id, payment_pkg_type,))) 
            else:
                return HttpResponseRedirect(reverse("my_saved_ad_more_details",args=(ad_id, property_ad_type)))
            
        except Buy_Item_Ad_Type.DoesNotExist:
            return render(request, "error.html", {"message": "Invalid ad type."})
    else:
        ad_types = Buy_Item_Ad_Type.objects.all()
        property_types = Property_Type.objects.all().order_by('name')
        bedrooms = range(1,7)
        bathrooms = range(1,7)
        parking = range(0,5)
        garages = range(0,5)
        context ={"ad_types":ad_types, "property_types":property_types, "bedrooms":bedrooms, "bathrooms":bathrooms, "parking":parking, "garages":garages}
        return render(request, "post_ad.html", context)

    
# edit details of already posted Live Ad
@login_required(login_url='login')
def edit_ad(request, ad_id, ad_type):
    ad_item = None
    try:
        if ad_type == 'rent':
            ad_item = Rent_Ad_Item.objects.get(user = request.user, pk = ad_id, payment=True)
        else:
            ad_item = Buy_Ad_Item.objects.get(user = request.user, pk = ad_id, payment=True)
            
        if not ad_item:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
    except Rent_Ad_Item.DoesNotExist:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
    except Buy_Ad_Item.DoesNotExist:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
    if request.method == "POST":
        try:
            if ad_type == 'rent':
                
                weekly_price = request.POST["weekly_price"]
                ad_item.weekly_price = float(weekly_price)
                
                title = request.POST["rent_title"]
                ad_item.title = title
                
                desc = request.POST["rent_description"]
                ad_item.desc = desc
                
                property_type = request.POST["rent_property_type"]
                ad_item.property_type = Property_Type.objects.get(code=property_type)
                
                address_line = request.POST["rent_address_line"]
                ad_item.address_line = address_line
                
                location_str = request.POST["rent_location"]
                if location_str:
                    location_data  = location_str.split(", ")
                    if len(location_data) == 3:
                        location = Location.objects.get(Q(postcode=location_data[2]) & Q(suburb=location_data[0]) & Q(state=location_data[1]))
                        if location:
                            ad_item.location = location
                        else:
                            return render(request, "error.html", {"message": "Invalid item location."})
                    else:
                        return render(request, "error.html", {"message": "Invalid item location."})
                else:
                    return render(request, "error.html", {"message": "Invalid item location."})
                
                bedrooms = request.POST["rent_bedrooms"]
                ad_item.bedrooms = int(bedrooms)
                
                bathrooms = request.POST["rent_bathrooms"]
                ad_item.bathrooms = int(bathrooms)
                
                parking = request.POST["rent_parking"]
                ad_item.parking = int(parking)
                
                garages = request.POST["rent_garages"]
                ad_item.garages = int(garages)
                
                contact_name = request.POST["rent_contact_name"]
                ad_item.contact_name = contact_name

                contact_email = request.POST["rent_contact_email"]
                ad_item.email = contact_email

                mobile = request.POST["rent_mobile"]
                ad_item.mobile = mobile
                
                floorplan = request.FILES.get('rent_floorplan')
                if floorplan:
                    ad_item.floorplan = floorplan
                
                ad_item.save()
                
                for i in range(1,7):
                    img = request.FILES.get('rent_img_' + str(i))
                    if img:
                        picture = Rent_Item_Picture()
                        picture.ad_item = ad_item
                        picture.image = img
                        picture.save()
                    
                insepctions = Rent_Item_Inspection.objects.filter(ad_item = ad_item).order_by('id')
                for i in range (1, len(insepctions)+1):
                    ins_date = request.POST.get('rent_ins_date_' + str(i))
                    ins_from_time = request.POST.get('rent_ins_from_time_' + str(i))
                    ins_to_time = request.POST.get('rent_ins_to_time_' + str(i))
                    if ins_date:
                        insepctions[i-1].date = datetime.strptime(ins_date, '%Y-%m-%d')
                        insepctions[i-1].from_time = datetime.strptime(ins_from_time, '%H:%M')
                        insepctions[i-1].to_time = datetime.strptime(ins_to_time, '%H:%M')
                        insepctions[i-1].save()
                        
                for i in range(len(insepctions)+1,5):
                    ins_date = request.POST.get('rent_ins_date_' + str(i))
                    ins_from_time = request.POST.get('rent_ins_from_time_' + str(i))
                    ins_to_time = request.POST.get('rent_ins_to_time_' + str(i))
                    
                    if ins_date:
                        insp = Rent_Item_Inspection()
                        insp.ad_item = ad_item
                        insp.date = datetime.strptime(ins_date, '%Y-%m-%d')
                        insp.from_time = datetime.strptime(ins_from_time, '%H:%M')
                        insp.to_time = datetime.strptime(ins_to_time, '%H:%M')
                        insp.save()
                
            else:
                
                from_price = request.POST["from_price"]
                if from_price:
                    ad_item.from_price = float(from_price)
                else:
                    ad_item.from_price = 0.0
                to_price = request.POST["to_price"]
                if to_price:
                    ad_item.to_price = float(to_price)
                else:
                    ad_item.to_price = 0.0
                ad_type = request.POST["ad_type"]
                ad_item.ad_type = Buy_Item_Ad_Type.objects.get(pk=ad_type)
                
                title = request.POST["title"]
                ad_item.title = title
                
                desc = request.POST["description"]
                ad_item.desc = desc
                
                property_type = request.POST["property_type"]
                ad_item.property_type = Property_Type.objects.get(code=property_type)
                
                action_date = request.POST["action_date"]
                if action_date:
                    ad_item.auction_date = datetime.strptime(action_date, '%Y-%m-%dT%H:%M')
                
                address_line = request.POST["address_line"]
                ad_item.address_line = address_line
                
                
                location_str = request.POST["location"]
                if location_str:
                    location_data  = location_str.split(", ")
                    if len(location_data) == 3:
                        location = Location.objects.get(Q(postcode=location_data[2]) & Q(suburb=location_data[0]) & Q(state=location_data[1]))
                        if location:
                            ad_item.location = location
                        else:
                            return render(request, "error.html", {"message": "Invalid item location."})
                    else:
                        return render(request, "error.html", {"message": "Invalid item location."})
                else:
                    return render(request, "error.html", {"message": "Invalid item location."})
                
                bedrooms = request.POST["bedrooms"]
                ad_item.bedrooms = int(bedrooms)
                
                bathrooms = request.POST["bathrooms"]
                ad_item.bathrooms = int(bathrooms)
                
                parking = request.POST["parking"]
                ad_item.parking = int(parking)
                
                garages = request.POST["garages"]
                ad_item.garages = int(garages)
                
                land_area = request.POST["land_area"]
                ad_item.land_area = land_area
                
                contact_name = request.POST["contact_name"]
                ad_item.contact_name = contact_name

                contact_email = request.POST["contact_email"]
                ad_item.email = contact_email

                mobile = request.POST["mobile"]
                ad_item.mobile = mobile
                
                floorplan = request.FILES.get('floorplan')
                if floorplan:
                    ad_item.floorplan = floorplan
            
                
                ad_item.save()
                
                for i in range(1,7):
                    img = request.FILES.get('img_' + str(i))
                    if img:
                        picture = Buy_Item_Picture()
                        picture.ad_item = ad_item
                        picture.image = img
                        picture.save()
                        
                insepctions = Buy_Item_Inspection.objects.filter(ad_item = ad_item).order_by('id')
                for i in range (1, len(insepctions)+1):
                    ins_date = request.POST.get('ins_date_' + str(i))
                    ins_from_time = request.POST.get('ins_from_time_' + str(i))
                    ins_to_time = request.POST.get('ins_to_time_' + str(i))
                    if ins_date:
                        insepctions[i-1].date = datetime.strptime(ins_date, '%Y-%m-%d')
                        insepctions[i-1].from_time = datetime.strptime(ins_from_time, '%H:%M')
                        insepctions[i-1].to_time = datetime.strptime(ins_to_time, '%H:%M')
                        insepctions[i-1].save()
                        
                for i in range(len(insepctions)+1,5):
                    ins_date = request.POST.get('ins_date_' + str(i))
                    ins_from_time = request.POST.get('ins_from_time_' + str(i))
                    ins_to_time = request.POST.get('ins_to_time_' + str(i))
                    
                    if ins_date:
                        insp = Buy_Item_Inspection()
                        insp.ad_item = ad_item
                        insp.date = datetime.strptime(ins_date, '%Y-%m-%d')
                        insp.from_time = datetime.strptime(ins_from_time, '%H:%M')
                        insp.to_time = datetime.strptime(ins_to_time, '%H:%M')
                        insp.save()
                
            return HttpResponseRedirect(reverse("my_ad_more_details",args=(ad_item.id, ad_type,)))    
        except Buy_Item_Ad_Type.DoesNotExist:
            return render(request, "error.html", {"message": "Invalid ad type."})
    else:
        pictures = None
        insepctions = None
        if ad_type == 'rent':
            pictures = Rent_Item_Picture.objects.filter(ad_item = ad_item).order_by('id')
            insepctions = Rent_Item_Inspection.objects.filter(ad_item = ad_item).order_by('id')
        else:
            pictures = Buy_Item_Picture.objects.filter(ad_item = ad_item).order_by('id')
            insepctions = Buy_Item_Inspection.objects.filter(ad_item = ad_item).order_by('id')
        if pictures:
            pic_loop_times = range(len(pictures)+1,7)
        else:
            pic_loop_times = range(1,7)
            
        if insepctions:
            insp_loop_times = range(len(insepctions)+1,5)
        else:
            insp_loop_times = range(1,5)
            
        ad_types = Buy_Item_Ad_Type.objects.all()
        property_types = Property_Type.objects.all().order_by('name')
        bedrooms = range(1,7)
        bathrooms = range(1,7)
        parking = range(0,5)
        garages = range(0,5)
        context ={"ad_type":ad_type, "ad_item":ad_item, "ad_types":ad_types, "property_types":property_types, "bedrooms":bedrooms, "bathrooms":bathrooms, "parking":parking, "garages":garages, "pictures":pictures, "pic_loop_times":pic_loop_times, "insepctions":insepctions, "insp_loop_times":insp_loop_times,}
        return render(request, "my_ad_edit.html", context)

    
# edit details of non-Live ads
@login_required(login_url='login')
def edit_saved_ad(request, ad_id, ad_property_type):
    ad_item = None
    try:
        if ad_property_type == 'rent':
            ad_item = Rent_Ad_Item.objects.get(user = request.user, pk = ad_id, payment=False)
        else:
            ad_item = Buy_Ad_Item.objects.get(user = request.user, pk = ad_id, payment=False)
            
        if not ad_item:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
    except Rent_Ad_Item.DoesNotExist:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
    except Buy_Ad_Item.DoesNotExist:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
    if request.method == "POST":
        try:
            payment_pkg = None;
            action = request.POST["action"]
            if ad_property_type == 'rent':
                
                weekly_price = request.POST["weekly_price"]
                ad_item.weekly_price = float(weekly_price)
                
                title = request.POST["rent_title"]
                ad_item.title = title
                
                desc = request.POST["rent_description"]
                ad_item.desc = desc
                
                property_type = request.POST["rent_property_type"]
                ad_item.property_type = Property_Type.objects.get(code=property_type)
                
                address_line = request.POST["rent_address_line"]
                ad_item.address_line = address_line
                
                location_str = request.POST["rent_location"]
                if location_str:
                    location_data  = location_str.split(", ")
                    if len(location_data) == 3:
                        location = Location.objects.get(Q(postcode=location_data[2]) & Q(suburb=location_data[0]) & Q(state=location_data[1]))
                        if location:
                            ad_item.location = location
                        else:
                            return render(request, "error.html", {"message": "Invalid item location."})
                    else:
                        return render(request, "error.html", {"message": "Invalid item location."})
                else:
                    return render(request, "error.html", {"message": "Invalid item location."})
                
                bedrooms = request.POST["rent_bedrooms"]
                ad_item.bedrooms = int(bedrooms)
                
                bathrooms = request.POST["rent_bathrooms"]
                ad_item.bathrooms = int(bathrooms)
                
                parking = request.POST["rent_parking"]
                ad_item.parking = int(parking)
                
                garages = request.POST["rent_garages"]
                ad_item.garages = int(garages)
                
                contact_name = request.POST["rent_contact_name"]
                ad_item.contact_name = contact_name

                contact_email = request.POST["rent_contact_email"]
                ad_item.email = contact_email

                mobile = request.POST["rent_mobile"]
                ad_item.mobile = mobile
                
                floorplan = request.FILES.get('rent_floorplan')
                if floorplan:
                    ad_item.floorplan = floorplan
                
                
                ad_item.save()
                
                for i in range(1,7):
                    img = request.FILES.get('rent_img_' + str(i))
                    if img:
                        picture = Rent_Item_Picture()
                        picture.ad_item = ad_item
                        picture.image = img
                        picture.save()
                    
                insepctions = Rent_Item_Inspection.objects.filter(ad_item = ad_item).order_by('id')
                for i in range (1, len(insepctions)+1):
                    ins_date = request.POST.get('rent_ins_date_' + str(i))
                    ins_from_time = request.POST.get('rent_ins_from_time_' + str(i))
                    ins_to_time = request.POST.get('rent_ins_to_time_' + str(i))
                    if ins_date:
                        insepctions[i-1].date = datetime.strptime(ins_date, '%Y-%m-%d')
                        insepctions[i-1].from_time = datetime.strptime(ins_from_time, '%H:%M')
                        insepctions[i-1].to_time = datetime.strptime(ins_to_time, '%H:%M')
                        insepctions[i-1].save()
                        
                for i in range(len(insepctions)+1,5):
                    ins_date = request.POST.get('rent_ins_date_' + str(i))
                    ins_from_time = request.POST.get('rent_ins_from_time_' + str(i))
                    ins_to_time = request.POST.get('rent_ins_to_time_' + str(i))
                    
                    if ins_date:
                        insp = Rent_Item_Inspection()
                        insp.ad_item = ad_item
                        insp.date = datetime.strptime(ins_date, '%Y-%m-%d')
                        insp.from_time = datetime.strptime(ins_from_time, '%H:%M')
                        insp.to_time = datetime.strptime(ins_to_time, '%H:%M')
                        insp.save()
                        
                    payment_pkg = request.POST["rent_payment_pkg"]
                    
            else:
                
                from_price = request.POST["from_price"]
                if from_price:
                    ad_item.from_price = float(from_price)
                else:
                    ad_item.from_price = 0.0
                to_price = request.POST["to_price"]
                if to_price:
                    ad_item.to_price = float(to_price)
                else:
                    ad_item.to_price = 0.0
                ad_type = request.POST["ad_type"]
                ad_item.ad_type = Buy_Item_Ad_Type.objects.get(pk=ad_type)
                
                title = request.POST["title"]
                ad_item.title = title
                
                desc = request.POST["description"]
                ad_item.desc = desc
                
                property_type = request.POST["property_type"]
                ad_item.property_type = Property_Type.objects.get(code=property_type)
                
                action_date = request.POST["action_date"]
                if action_date:
                    ad_item.auction_date = datetime.strptime(action_date, '%Y-%m-%dT%H:%M')
                
                address_line = request.POST["address_line"]
                ad_item.address_line = address_line
                
                
                location_str = request.POST["location"]
                if location_str:
                    location_data  = location_str.split(", ")
                    if len(location_data) == 3:
                        location = Location.objects.get(Q(postcode=location_data[2]) & Q(suburb=location_data[0]) & Q(state=location_data[1]))
                        if location:
                            ad_item.location = location
                        else:
                            return render(request, "error.html", {"message": "Invalid item location."})
                    else:
                        return render(request, "error.html", {"message": "Invalid item location."})
                else:
                    return render(request, "error.html", {"message": "Invalid item location."})
                
                bedrooms = request.POST["bedrooms"]
                ad_item.bedrooms = int(bedrooms)
                
                bathrooms = request.POST["bathrooms"]
                ad_item.bathrooms = int(bathrooms)
                
                parking = request.POST["parking"]
                ad_item.parking = int(parking)
                
                garages = request.POST["garages"]
                ad_item.garages = int(garages)
                
                land_area = request.POST["land_area"]
                ad_item.land_area = land_area
                
                contact_name = request.POST["contact_name"]
                ad_item.contact_name = contact_name

                contact_email = request.POST["contact_email"]
                ad_item.email = contact_email

                mobile = request.POST["mobile"]
                ad_item.mobile = mobile
                
                floorplan = request.FILES.get('floorplan')
                if floorplan:
                    ad_item.floorplan = floorplan
            
                
                ad_item.save()
                
                for i in range(1,7):
                    img = request.FILES.get('img_' + str(i))
                    if img:
                        picture = Buy_Item_Picture()
                        picture.ad_item = ad_item
                        picture.image = img
                        picture.save()
                        
                insepctions = Buy_Item_Inspection.objects.filter(ad_item = ad_item).order_by('id')
                for i in range (1, len(insepctions)+1):
                    ins_date = request.POST.get('ins_date_' + str(i))
                    ins_from_time = request.POST.get('ins_from_time_' + str(i))
                    ins_to_time = request.POST.get('ins_to_time_' + str(i))
                    if ins_date:
                        insepctions[i-1].date = datetime.strptime(ins_date, '%Y-%m-%d')
                        insepctions[i-1].from_time = datetime.strptime(ins_from_time, '%H:%M')
                        insepctions[i-1].to_time = datetime.strptime(ins_to_time, '%H:%M')
                        insepctions[i-1].save()
                        
                for i in range(len(insepctions)+1,5):
                    ins_date = request.POST.get('ins_date_' + str(i))
                    ins_from_time = request.POST.get('ins_from_time_' + str(i))
                    ins_to_time = request.POST.get('ins_to_time_' + str(i))
                    
                    if ins_date:
                        insp = Buy_Item_Inspection()
                        insp.ad_item = ad_item
                        insp.date = datetime.strptime(ins_date, '%Y-%m-%d')
                        insp.from_time = datetime.strptime(ins_from_time, '%H:%M')
                        insp.to_time = datetime.strptime(ins_to_time, '%H:%M')
                        insp.save()
                        
                payment_pkg = request.POST["payment_pkg"]
                
            if action == 'payment':    
                return HttpResponseRedirect(reverse("payment",args=(ad_property_type, ad_id, payment_pkg,))) 
            else:
                return HttpResponseRedirect(reverse("my_saved_ad_more_details",args=(ad_id, ad_property_type)))
            
        except Buy_Item_Ad_Type.DoesNotExist:
            return render(request, "error.html", {"message": "Invalid ad type."})
    else:
        pictures = None
        insepctions = None
        if ad_property_type == 'rent':
            pictures = Rent_Item_Picture.objects.filter(ad_item = ad_item).order_by('id')
            insepctions = Rent_Item_Inspection.objects.filter(ad_item = ad_item).order_by('id')
        else:
            pictures = Buy_Item_Picture.objects.filter(ad_item = ad_item).order_by('id')
            insepctions = Buy_Item_Inspection.objects.filter(ad_item = ad_item).order_by('id')
        if pictures:
            pic_loop_times = range(len(pictures)+1,7)
        else:
            pic_loop_times = range(1,7)
            
        if insepctions:
            insp_loop_times = range(len(insepctions)+1,5)
        else:
            insp_loop_times = range(1,5)
            
        ad_types = Buy_Item_Ad_Type.objects.all()
        property_types = Property_Type.objects.all().order_by('name')
        bedrooms = range(1,7)
        bathrooms = range(1,7)
        parking = range(0,5)
        garages = range(0,5)
        context ={"ad_property_type":ad_property_type, "ad_item":ad_item, "ad_types":ad_types, "property_types":property_types, "bedrooms":bedrooms, "bathrooms":bathrooms, "parking":parking, "garages":garages, "pictures":pictures, "pic_loop_times":pic_loop_times, "insepctions":insepctions, "insp_loop_times":insp_loop_times,}
        return render(request, "my_saved_ad_edit.html", context)

    
 # delete already uploaded photos
@login_required(login_url='login')
def delete_pic(request, ad_id, ad_type, pic_id,pic_type):
    ad_item = None
    try:
        if ad_type == 'rent':
            if pic_type == 'live':
                ad_item = Rent_Ad_Item.objects.get(user = request.user, pk = ad_id, payment=True)
            else:
                ad_item = Rent_Ad_Item.objects.get(user = request.user, pk = ad_id, payment=False)
        else:
            if pic_type == 'live':
                ad_item = Buy_Ad_Item.objects.get(user = request.user, pk = ad_id, payment=True)
            else:
                ad_item = Buy_Ad_Item.objects.get(user = request.user, pk = ad_id, payment=False)
            
        if not ad_item:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
        
        if ad_type == 'rent':
            picture = Rent_Item_Picture.objects.get(ad_item = ad_item, pk = pic_id )
            if not picture:
                return render(request, "error.html", {"message": "You are not authorised to update this item"})
            picture.delete()
        else:
            picture = Buy_Item_Picture.objects.get(ad_item = ad_item, pk = pic_id )
            if not picture:
                return render(request, "error.html", {"message": "You are not authorised to update this item"})
            picture.delete()
            
    except Rent_Ad_Item.DoesNotExist:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
    except Buy_Ad_Item.DoesNotExist:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
    
    if pic_type == 'live':
        return HttpResponseRedirect(reverse("edit_ad", args=[ad_id, ad_type]))
    else:
        return HttpResponseRedirect(reverse("edit_saved_ad", args=[ad_id, ad_type]))

    
# delete already uploaded floorplan
@login_required(login_url='login')
def delete_floorplan(request, ad_id, ad_type ,pic_type):
    ad_item = None
    try:
        if ad_type == 'rent':
            if pic_type == 'live':
                ad_item = Rent_Ad_Item.objects.get(user = request.user, pk = ad_id, payment=True)
            else:
                ad_item = Rent_Ad_Item.objects.get(user = request.user, pk = ad_id, payment=False)
        else:
            if pic_type == 'live':
                ad_item = Buy_Ad_Item.objects.get(user = request.user, pk = ad_id, payment=True)
            else:
                ad_item = Buy_Ad_Item.objects.get(user = request.user, pk = ad_id, payment=False)
            
        if not ad_item:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
        
        ad_item.floorplan = ""
        ad_item.save()
            
    except Rent_Ad_Item.DoesNotExist:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
    except Buy_Ad_Item.DoesNotExist:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
    if pic_type == 'live':
        return HttpResponseRedirect(reverse("edit_ad", args=[ad_id, ad_type]))
    else:
        return HttpResponseRedirect(reverse("edit_saved_ad", args=[ad_id, ad_type]))
    
    
# payemnt redirection processing page, Stripe products and prices were created upfront using its dashboard
@login_required(login_url='login')
def payment(request, ad_type, ad_id, payment_pkg):

    try:
        ad_item= None
        price_id  = None
        if ad_type == 'rent':
            ad_item = Rent_Ad_Item.objects.get(pk=ad_id, user=request.user)
            # Stripe products and prices were created upfront, below ids copied from dashbaord in order to retrive
            if payment_pkg == 'STD':
                price_id ='price_1GwIGDCyCCbzUhmXeOTQChz5'
            else:
                price_id ='price_1GwIGiCyCCbzUhmXVUeCdM9P'
        else:
            ad_item = Buy_Ad_Item.objects.get(pk=ad_id, user=request.user)
            if payment_pkg == 'STD':
                price_id ='price_1GwIDeCyCCbzUhmXO6YiTDU7' 
            else:
                price_id ='price_1GwIFKCyCCbzUhmXKBti8Q8R'
                
        if not ad_item or not price_id:
            return render(request, "error.html", {"message": "Invalid request."})
        else:
            price = stripe.Price.retrieve(price_id)
            
            if not price:
                return render(request, "error.html", {"message": "Invalid request."})

            stripe_price_items = {"price":price.id,'quantity': 1,}
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[stripe_price_items],
                mode='payment',
                success_url=getattr(settings, "PAYMENT_SUCCESS_URL", None),
                cancel_url=getattr(settings, "PAYMENT_CANCEL_URL", None),
            )
            
            context = {"STRIPE_PUBLISHABLE_API_KEY":getattr(settings, "STRIPE_PUBLISHABLE_API_KEY", None),"CHECKOUT_SESSION_ID":session.id,}
            request.session['AD_ID'] = ad_id
            request.session['AD_TYPE'] = ad_type
            request.session['PAYMENT_PKG'] = payment_pkg
            request.session['CHECKOUT_SESSION_ID'] = session.id
            
            return render(request, "payment.html", context)
    except stripe.error.InvalidRequestError:
        render(request, "error.html", {"message": "Invalid request."})

        
# stripe payment success page           
@login_required(login_url='login')
def payment_success(request):
    
    # when stripe payment is success, it will redirect here
    # TODO :: we need to integrate stripe WEBHOOK before redirect here, since webhook can not setup with local host I havent integrate it yet
    # check session ids are equal
    payment_session_id = request.session['CHECKOUT_SESSION_ID']
    
    session_id_from_url = ""
    try:
        session_id_from_url = request.GET["session_id"]
    except KeyError:
        return render(request, "error.html", {"message": "Invalid request."})
    if payment_session_id != session_id_from_url:
        return render(request, "error.html", {"message": "Invalid request."})
    
    ad_id = request.session['AD_ID']
    ad_type = request.session['AD_TYPE']
    payment_pkg = request.session['PAYMENT_PKG']
    
    if ad_type == 'rent':
        ad_item = Rent_Ad_Item.objects.get(pk=ad_id, user=request.user)
        if not ad_item:
            return render(request, "error.html", {"message": "Invalid request."})
        ad_item.payment = True
        ad_item.payemnt_session = payment_session_id
        if payment_pkg == 'PRM':
            ad_item.payment_pkg = 'PRM'
            ad_item.priority = 2
            ad_item.amount_paid = 400
        else:
            ad_item.payment_pkg = 'STD'
            ad_item.priority = 1
            ad_item.amount_paid = 250
        ad_item.save()
    else:
        ad_item = Buy_Ad_Item.objects.get(pk=ad_id, user=request.user)
        if not ad_item:
            return render(request, "error.html", {"message": "Invalid request."})
        ad_item.payment = True
        ad_item.payemnt_session = payment_session_id
        if payment_pkg == 'PRM':
            ad_item.payment_pkg = 'PRM'
            ad_item.priority = 2
            ad_item.amount_paid = 1000
        else:
            ad_item.payment_pkg = 'STD'
            ad_item.priority = 1
            ad_item.amount_paid = 750
        ad_item.save()
        
        #clear session values
        request.session['AD_ID'] = None
        request.session['AD_TYPE'] = None
        request.session['PAYMENT_PKG'] = None
        request.session['CHECKOUT_SESSION_ID'] = None
        
    return HttpResponseRedirect(reverse("my_ad_more_details",args=(ad_item.id, ad_type,)))


# stripe payment cancel page
@login_required(login_url='login')
def payment_cancel(request):
    ad_id = request.session['AD_ID']
    ad_type = request.session['AD_TYPE']
    return HttpResponseRedirect(reverse("my_saved_ad_more_details",args=(ad_id, ad_type,)))


# for saved ads which are not paid, will have a “Pay Now” link. Once clicked on this link user will be taken to this view where they can select the ad package depending on rent ad or sale item and pay for it in order to make the Ad live
   
@login_required(login_url='login')
def payment_packages(request,ad_id, ad_type):
    try:
        if ad_type == 'rent':
            ad_item = Rent_Ad_Item.objects.get(user = request.user, pk = ad_id)
        else:
            ad_item = Buy_Ad_Item.objects.get(user = request.user, pk = ad_id)
            
        if not ad_item:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
    except Rent_Ad_Item.DoesNotExist:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
    except Buy_Ad_Item.DoesNotExist:
            return render(request, "error.html", {"message": "You are not authorised to update this item"})
    if request.method == "POST":
        if ad_type == 'rent':
            payment_pkg = request.POST["rent_payment_pkg"]
        else:
            payment_pkg = request.POST["payment_pkg"]
            
        ad_id = ad_item.id
        property_ad_type = ad_type
        payment_pkg_type = payment_pkg
        return HttpResponseRedirect(reverse("payment",args=(property_ad_type, ad_id, payment_pkg_type,))) 
    
    else:
        context = {"ad_id":ad_id,"ad_type":ad_type,}
        return render(request, "payment_pkg.html", context)

    
# view Live Ads posted by login user
@login_required(login_url='login')
def view_my_ads(request):
    search_type = request.GET.get('search_type','')
    ad_items = None
    dict_photo_items = {}
    if search_type and search_type == 'rent':
        ad_items = Rent_Ad_Item.objects.filter(user=request.user, payment=True).order_by('-date_time')

        for rent_ad_item in ad_items:
            # laod photos for each ad item
            photo_items = Rent_Item_Picture.objects.filter(ad_item =rent_ad_item)
            if photo_items:
                dict_photo_items[rent_ad_item.id] = photo_items
    else:
        search_type = 'sale'
        ad_items = Buy_Ad_Item.objects.filter(user=request.user, payment=True).order_by('-date_time')

        for buy_ad_item in ad_items:
            # laod photos for each ad item
            photo_items = Buy_Item_Picture.objects.filter(ad_item =buy_ad_item)
            if photo_items:
                dict_photo_items[buy_ad_item.id] = photo_items 
                    
    context ={"ad_items":ad_items, "photo_items":dict_photo_items,"search_type":search_type,}
    return render(request, "my_ads.html", context)


# view saved non-Live Ads posted by login user
@login_required(login_url='login')
def view_my_saved_ads(request):
    search_type = request.GET.get('search_type','')
    ad_items = None
    dict_photo_items = {}
    if search_type and search_type == 'rent':
        ad_items = Rent_Ad_Item.objects.filter(user=request.user, payment=False).order_by('-date_time')

        for rent_ad_item in ad_items:
            # laod photos for each ad item
            photo_items = Rent_Item_Picture.objects.filter(ad_item =rent_ad_item)
            if photo_items:
                dict_photo_items[rent_ad_item.id] = photo_items
    else:
        search_type = 'sale'
        ad_items = Buy_Ad_Item.objects.filter(user=request.user, payment=False).order_by('-date_time')

        for buy_ad_item in ad_items:
            # laod photos for each ad item
            photo_items = Buy_Item_Picture.objects.filter(ad_item =buy_ad_item)
            if photo_items:
                dict_photo_items[buy_ad_item.id] = photo_items 
                    
    context ={"ad_items":ad_items, "photo_items":dict_photo_items,"search_type":search_type,}
    return render(request, "my_saved_ads.html", context)
