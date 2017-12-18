# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-18 02:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20171218_0022'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='allowancegroup',
            name='allowance',
        ),
        migrations.RemoveField(
            model_name='allowancegroup',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='allowance',
            name='members',
        ),
        migrations.AddField(
            model_name='employee',
            name='allowance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='members', to='dashboard.Allowance'),
        ),
        migrations.AlterField(
            model_name='allowance',
            name='name',
            field=models.CharField(blank=True, default="b'9ad4f131ed10b0bec97'-DarkOrchid-Ryan-Pike", max_length=100, null=True),
        ),
        migrations.DeleteModel(
            name='AllowanceGroup',
        ),
    ]
