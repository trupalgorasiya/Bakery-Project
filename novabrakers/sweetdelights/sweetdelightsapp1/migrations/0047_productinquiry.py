# Generated by Django 5.1.2 on 2025-03-03 12:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0046_order_discount_order_discount_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductInquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('response', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sweetdelightsapp1.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sweetdelightsapp1.user')),
            ],
        ),
    ]
