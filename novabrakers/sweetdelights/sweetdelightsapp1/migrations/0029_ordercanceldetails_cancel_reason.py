# Generated by Django 5.1.2 on 2025-02-18 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0028_ordercancel_refund_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordercanceldetails',
            name='cancel_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
