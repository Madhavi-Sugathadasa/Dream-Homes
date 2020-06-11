from django.contrib import admin
from .models import Location, Property_Type, Bedroom, Bathroom, Parking, Buy_Item_Ad_Type, Buy_Ad_Item, Buy_Item_Picture, Buy_Item_Inspection, Rent_Ad_Item, Rent_Item_Picture

# Register your models here.
admin.site.register(Location)
admin.site.register(Property_Type)
admin.site.register(Bedroom)
admin.site.register(Bathroom)
admin.site.register(Parking)
admin.site.register(Buy_Item_Ad_Type)
admin.site.register(Buy_Ad_Item)
admin.site.register(Buy_Item_Picture)
admin.site.register(Buy_Item_Inspection)
admin.site.register(Rent_Ad_Item)
admin.site.register(Rent_Item_Picture)
