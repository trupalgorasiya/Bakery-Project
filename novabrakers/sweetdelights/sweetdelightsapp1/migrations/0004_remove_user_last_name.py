# Generated by Django 5.1.2 on 2025-01-27 07:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0003_user_confirm_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='last_name',
        ),
    ]
