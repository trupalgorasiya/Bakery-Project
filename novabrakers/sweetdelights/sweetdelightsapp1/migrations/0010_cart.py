# Generated by Django 5.1.2 on 2025-02-05 12:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0009_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('cart_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sweetdelightsapp1.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sweetdelightsapp1.user')),
            ],
        ),
    ]
