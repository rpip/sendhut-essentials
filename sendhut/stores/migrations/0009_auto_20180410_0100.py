# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-10 01:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0008_auto_20180409_1209'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='user',
        ),
        migrations.RemoveField(
            model_name='orderline',
            name='item',
        ),
        migrations.RemoveField(
            model_name='orderline',
            name='order',
        ),
        migrations.DeleteModel(
            name='Order',
        ),
        migrations.DeleteModel(
            name='OrderLine',
        ),
    ]
