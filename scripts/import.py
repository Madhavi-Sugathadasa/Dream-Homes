import csv
from dream_homes.models import Location
from django.conf import settings

# insert data in to the location table by reading the csv file
def run():
    
    with open(getattr(settings, "BASE_DIR", None) + "/australian_postcodes.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['long'] != 0 and row['lat'] !=0:
                location = Location()
                location.postcode = row['postcode']
                location.suburb = row['locality']
                location.state = row['state']
                location.lon = row['long']
                location.lat = row['lat']
                location.save() 
                print(location.postcode + " added")
    
