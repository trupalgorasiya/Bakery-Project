# Generated by Django 5.1.2 on 2025-02-24 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0029_ordercanceldetails_cancel_reason'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderreturn',
            name='refund_status',
        ),
        migrations.AddField(
            model_name='orderreturndetails',
            name='refund_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Processed', 'Processed'), ('Not Applicable', 'Not Applicable')], default='Pending', max_length=20),
        ),
    ]
