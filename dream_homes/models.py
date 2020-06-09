from django.db import models
from django.contrib.auth.models import User
from django.conf import settings as conf_settings
from datetime import datetime 

# Create your models here.
class Location(models.Model):
    postcode = models.CharField(max_length=8)
    suburb = models.CharField(max_length=20)
    state = models.CharField(max_length=5)
    lon = models.FloatField(null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.suburb}, {self.state}, {self.postcode}"
    
    
class Property_Type(models.Model):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=64)
    def __str__(self):
        return f"{self.name} - {self.code}"
    
class Bedroom(models.Model):
    code = models.IntegerField(default=0)
    name = models.CharField(max_length=5)
    def __str__(self):
        return f"{self.name}"
    
    
class Bathroom(models.Model):
    code = models.IntegerField(default=0)
    name = models.CharField(max_length=5)
    def __str__(self):
        return f"{self.name}"

    
class Parking(models.Model):
    code = models.IntegerField(default=0)
    name = models.CharField(max_length=5)
    def __str__(self):
        return f"{self.name}"
    
class Buy_Item_Ad_Type(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return f"{self.name}"
    
class Buy_Ad_Item(models.Model):
    def _image_path_(self, filename):
        return (conf_settings.MEDIA_PATH + '/buy_properties/{0}/{1}').format(self.id, filename)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buy_ad_user")
    from_price = models.FloatField(null=True, blank=True)
    to_price = models.FloatField(null=True, blank=True)
    ad_type = models.ForeignKey(Buy_Item_Ad_Type, on_delete=models.DO_NOTHING, related_name="buy_item_ad_type")
    title = models.CharField(max_length=200)
    desc = models.CharField(max_length=4000)
    property_type = models.ForeignKey(Property_Type, on_delete=models.DO_NOTHING, related_name="buy_ad_property_type")
    address_line = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING, related_name="buy_ad_location", default="")
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    parking = models.IntegerField(default=1)
    garages = models.IntegerField(default=0)
    floorplan = models.ImageField(upload_to = _image_path_, default="", null=True, blank=True)
    land_area = models.CharField(max_length=64, null=True, blank=True)
    contact_name = models.CharField(max_length=64, default="")
    email = models.CharField(max_length=64, default="")
    mobile = models.CharField(max_length=64, default="")
    date_time = models.DateTimeField()
    active = models.BooleanField(default=True)
    auction_date = models.DateTimeField(null=True, blank=True)
    priority  = models.IntegerField(default=1)
    payment = models.BooleanField(default=False)
    payment_pkg = models.CharField(max_length=4,default="")
    amount_paid = models.FloatField(default=0.0)
    payemnt_session = models.CharField(max_length=200,default="")
    
    def __str__(self):
        return f"{self.id}: - {self.address_line}, {self.location}"
 

  
def buy_item_photo_path_(instance, filename):
    return (conf_settings.MEDIA_PATH + '/buy_properties/{0}/{1}').format(instance.ad_item.id, filename)

class Buy_Item_Picture(models.Model):
    ad_item = models.ForeignKey(Buy_Ad_Item, on_delete=models.CASCADE, related_name="buy_ad_item")
    image = models.ImageField(upload_to = buy_item_photo_path_)
    
    def __str__(self):
        return f"{self.image}"