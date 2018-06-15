# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-06-07 00:31
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20180412_1727'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='apt_number',
        ),
        migrations.RemoveField(
            model_name='address',
            name='instructions',
        ),
        migrations.AddField(
            model_name='address',
            name='apt',
            field=models.CharField(blank=True, max_length=42, null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(geography=True, null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='address',
            name='notes',
            field=models.CharField(blank=True, max_length=252, null=True),
        ),
    ]