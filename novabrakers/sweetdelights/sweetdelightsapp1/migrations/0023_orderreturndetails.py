# Generated by Django 5.1.2 on 2025-02-13 12:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0022_orderreturn'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderReturnDetails',
            fields=[
                ('return_detail_id', models.AutoField(primary_key=True, serialize=False)),
                ('quantity_returned', models.PositiveIntegerField(default=1)),
                ('order_detail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sweetdelightsapp1.orderdetails')),
                ('order_return', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sweetdelightsapp1.orderreturn')),
            ],
        ),
    ]
