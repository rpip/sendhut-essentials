# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-14 18:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0008_auto_20180114_1727'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupcart',
            name='cart',
        ),
        migrations.AddField(
            model_name='groupcart',
            name='name',
            field=models.CharField(default='warm-coast-1', max_length=20),
            preserve_default=False,
        ),
    ]