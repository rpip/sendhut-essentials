# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-06-11 17:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0008_remove_order_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='group_order',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order', to='giveaways.Coupon'),
        ),
    ]