# Generated by Django 5.1.6 on 2025-03-24 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0057_ingredient_productingredient_product_ingredients'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdetails',
            name='cake_customization',
            field=models.TextField(blank=True, null=True),
        ),
    ]
