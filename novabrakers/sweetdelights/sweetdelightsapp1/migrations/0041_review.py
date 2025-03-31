# Generated by Django 5.1.2 on 2025-03-01 16:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0040_productpayment_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=5)),
                ('comment', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sweetdelightsapp1.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sweetdelightsapp1.user')),
            ],
        ),
    ]
