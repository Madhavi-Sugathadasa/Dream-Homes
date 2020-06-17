# Generated by Django 2.1.5 on 2020-06-26 10:49

from django.db import migrations, models
import dream_homes.models


class Migration(migrations.Migration):

    dependencies = [
        ('dream_homes', '0011_auto_20200626_0216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buy_ad_item',
            name='floorplan',
            field=models.ImageField(blank=True, default='', null=True, upload_to=dream_homes.models.Buy_Ad_Item._image_path_),
        ),
        migrations.AlterField(
            model_name='rent_ad_item',
            name='floorplan',
            field=models.ImageField(blank=True, default='', null=True, upload_to=dream_homes.models.Rent_Ad_Item._image_path_),
        ),
    ]