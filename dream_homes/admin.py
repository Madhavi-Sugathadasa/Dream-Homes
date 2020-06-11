from django.contrib import admin
from .models import Location, Property_Type, Bedroom, Bathroom

# Register your models here.
admin.site.register(Location)
admin.site.register(Property_Type)
admin.site.register(Bedroom)
admin.site.register(Bathroom)
