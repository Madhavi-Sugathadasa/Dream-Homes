# Generated by Django 2.1.5 on 2020-06-19 03:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dream_homes', '0005_auto_20200618_0312'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buy_item_inspection',
            name='date_time',
        ),
        migrations.RemoveField(
            model_name='rent_item_inspection',
            name='date_time',
        ),
        migrations.AddField(
            model_name='buy_item_inspection',
            name='date',
            field=models.DateField(default=datetime.datetime(2020, 6, 19, 3, 56, 13, 227633)),
        ),
        migrations.AddField(
            model_name='buy_item_inspection',
            name='from_time',
            field=models.TimeField(default='15:00'),
        ),
        migrations.AddField(
            model_name='buy_item_inspection',
            name='to_time',
            field=models.TimeField(default='15:30'),
        ),
        migrations.AddField(
            model_name='rent_item_inspection',
            name='date',
            field=models.DateField(default=datetime.datetime(2020, 6, 19, 3, 56, 13, 229154)),
        ),
        migrations.AddField(
            model_name='rent_item_inspection',
            name='from_time',
            field=models.TimeField(default='15:00'),
        ),
        migrations.AddField(
            model_name='rent_item_inspection',
            name='to_time',
            field=models.TimeField(default='15:30'),
        ),
    ]
