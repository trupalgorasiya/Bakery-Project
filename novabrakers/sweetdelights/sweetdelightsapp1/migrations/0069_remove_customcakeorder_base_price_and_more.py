# Generated by Django 5.1.2 on 2025-03-26 06:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0068_customcakeorder_base_price_customcakeorder_discount_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customcakeorder',
            name='base_price',
        ),
        migrations.RemoveField(
            model_name='customcakeorder',
            name='discount_amount',
        ),
        migrations.RemoveField(
            model_name='customcakeorder',
            name='discount_code',
        ),
    ]
