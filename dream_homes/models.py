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