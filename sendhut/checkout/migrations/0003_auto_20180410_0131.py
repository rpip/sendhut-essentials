# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-10 01:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0002_auto_20180410_0126'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='total',
        ),
        migrations.RemoveField(
            model_name='order',
            name='total_currency',
        ),
    ]