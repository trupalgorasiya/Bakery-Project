# Generated by Django 5.1.2 on 2025-03-01 13:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0038_alter_productpayment_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productpayment',
            name='user',
        ),
    ]
