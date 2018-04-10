# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-09 12:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='address_1',
        ),
        migrations.RemoveField(
            model_name='address',
            name='address_2',
        ),
        migrations.RemoveField(
            model_name='address',
            name='address_3',
        ),
        migrations.RemoveField(
            model_name='address',
            name='city',
        ),
        migrations.RemoveField(
            model_name='address',
            name='county',
        ),
        migrations.RemoveField(
            model_name='address',
            name='location',
        ),
        migrations.RemoveField(
            model_name='address',
            name='postcode',
        ),
        migrations.AddField(
            model_name='address',
            name='address',
            field=models.CharField(default=None, max_length=120),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='apt_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='instructions',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='name',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
