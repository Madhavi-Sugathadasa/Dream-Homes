# Generated by Django 2.1.5 on 2020-06-18 03:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dream_homes', '0004_auto_20200618_0301'),
    ]

    operations = [
        migrations.RenameField(
            model_name='buy_ad_item',
            old_name='bathroom',
            new_name='bathrooms',
        ),
        migrations.RenameField(
            model_name='buy_ad_item',
            old_name='bedroom',
            new_name='bedrooms',
        ),
    ]
