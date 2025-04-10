# Generated by Django 5.1.2 on 2025-03-01 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0041_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='reviews/'),
        ),
        migrations.AddField(
            model_name='review',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]
