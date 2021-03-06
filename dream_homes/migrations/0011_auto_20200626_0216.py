# Generated by Django 2.1.5 on 2020-06-26 02:16

from django.db import migrations, models
import dream_homes.models


class Migration(migrations.Migration):

    dependencies = [
        ('dream_homes', '0010_auto_20200622_0425'),
    ]

    operations = [
        migrations.AddField(
            model_name='buy_ad_item',
            name='floorplan',
            field=models.ImageField(default='', upload_to=dream_homes.models.Buy_Ad_Item._image_path_),
        ),
        migrations.AddField(
            model_name='rent_ad_item',
            name='floorplan',
            field=models.ImageField(default='', upload_to=dream_homes.models.Rent_Ad_Item._image_path_),
        ),
    ]
