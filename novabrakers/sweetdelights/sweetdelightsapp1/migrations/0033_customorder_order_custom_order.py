# Generated by Django 5.1.2 on 2025-02-28 15:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sweetdelightsapp1', '0032_remove_orderreturn_return_reason_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cake_size', models.CharField(blank=True, max_length=50, null=True)),
                ('flavor', models.CharField(blank=True, max_length=50, null=True)),
                ('filling', models.CharField(blank=True, max_length=50, null=True)),
                ('topping', models.CharField(blank=True, max_length=50, null=True)),
                ('layers', models.CharField(blank=True, max_length=50, null=True)),
                ('theme', models.CharField(blank=True, max_length=50, null=True)),
                ('color', models.CharField(blank=True, max_length=50, null=True)),
                ('dietary', models.CharField(blank=True, max_length=50, null=True)),
                ('hidden_filling', models.CharField(blank=True, max_length=50, null=True)),
                ('topper', models.CharField(blank=True, max_length=100, null=True)),
                ('gift_message', models.TextField(blank=True, null=True)),
                ('additional_notes', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('admin_response', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sweetdelightsapp1.user')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='custom_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sweetdelightsapp1.customorder'),
        ),
    ]
