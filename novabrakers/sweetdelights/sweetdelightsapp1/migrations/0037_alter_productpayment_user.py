# Generated by Django 5.1.2 on 2025-03-01 13:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0036_productpayment_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productpayment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sweetdelightsapp1.user'),
        ),
    ]
