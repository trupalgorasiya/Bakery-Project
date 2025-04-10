# Generated by Django 5.1.2 on 2025-03-22 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0052_customorder_admin_notes_customorder_paid_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customorder',
            name='paid_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='customorder',
            name='total_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
