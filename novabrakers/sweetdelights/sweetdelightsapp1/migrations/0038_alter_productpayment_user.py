# Generated by Django 5.1.2 on 2025-03-01 13:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0037_alter_productpayment_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productpayment',
            name='user',
            field=models.ForeignKey(default=10, on_delete=django.db.models.deletion.CASCADE, to='sweetdelightsapp1.user'),
            preserve_default=False,
        ),
    ]
