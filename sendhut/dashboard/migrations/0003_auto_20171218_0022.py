# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-18 00:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0002_auto_20171211_2214'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, unique=True)),
                ('invite_token', models.CharField(max_length=32)),
                ('date_joined', models.DateTimeField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='allowance',
            name='name',
            field=models.CharField(blank=True, default="b'410d110b4d9b7b801de'-SpringGreen-Emily-Ways", max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.Address'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='role',
            field=models.IntegerField(blank=True, choices=[(0, 'Member'), (1, 'Admin')], default=0, null=True),
        ),
        migrations.AddField(
            model_name='invite',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invited_employees', to='dashboard.Company'),
        ),
        migrations.AddField(
            model_name='invite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
