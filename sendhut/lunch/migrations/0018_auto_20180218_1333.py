# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-18 13:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0017_auto_20180217_2216'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupcart',
            name='alias',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='groupcartmember',
            name='role',
            field=models.IntegerField(choices=[(1, 'Member'), (2, 'Admin')], default=1),
        ),
    ]