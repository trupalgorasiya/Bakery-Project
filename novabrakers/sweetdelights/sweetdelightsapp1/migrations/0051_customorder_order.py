# Generated by Django 5.1.2 on 2025-03-22 06:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0050_cakelayer_cakesize_dietary_filling_flavor_topping_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customorder',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sweetdelightsapp1.order'),
        ),
    ]
