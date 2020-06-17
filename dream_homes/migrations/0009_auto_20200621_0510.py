# Generated by Django 2.1.5 on 2020-06-21 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dream_homes', '0008_buy_item_inspection_rent_item_inspection'),
    ]

    operations = [
        migrations.AddField(
            model_name='buy_ad_item',
            name='payemnt_session',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='buy_ad_item',
            name='payment',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='buy_ad_item',
            name='priority',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='rent_ad_item',
            name='payemnt_session',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='rent_ad_item',
            name='payment',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rent_ad_item',
            name='priority',
            field=models.IntegerField(default=1),
        ),
    ]
