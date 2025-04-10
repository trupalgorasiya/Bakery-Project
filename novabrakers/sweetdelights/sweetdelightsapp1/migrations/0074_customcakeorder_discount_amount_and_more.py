# Generated by Django 5.1.2 on 2025-03-26 07:44

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0073_customcakeorder_discount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customcakeorder',
            name='discount_amount',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10),
        ),
        migrations.AddField(
            model_name='customcakeorder',
            name='discount_code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
