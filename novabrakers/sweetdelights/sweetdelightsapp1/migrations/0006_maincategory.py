# Generated by Django 5.1.2 on 2025-01-30 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0005_alter_user_confirm_password_alter_user_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='MainCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
    ]
