# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-18 20:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0019_auto_20180218_1827'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupcart',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='groupcartmember',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='image',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='item',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='itemimage',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='menu',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='menuoption',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='option',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='optiongroup',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='order',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='orderline',
            name='deleted_at',
        ),
        migrations.RemoveField(
            model_name='vendor',
            name='deleted_at',
        ),
    ]