# Generated by Django 5.1.2 on 2025-03-26 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0064_customcakeorder_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customcakeorder',
            name='pickup_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customcakeorder',
            name='pickup_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
