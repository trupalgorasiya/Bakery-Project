# Generated by Django 5.1.2 on 2025-02-07 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0012_alter_cart_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together={('user', 'product', 'selected_price_option')},
        ),
    ]
