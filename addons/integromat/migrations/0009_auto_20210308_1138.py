# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2021-03-08 11:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addons_integromat', '0008_auto_20210225_0726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allmeetinginformation',
            name='content',
            field=models.TextField(blank=True, max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='allmeetinginformation',
            name='join_url',
            field=models.TextField(max_length=512),
        ),
        migrations.AlterField(
            model_name='allmeetinginformation',
            name='location',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='allmeetinginformation',
            name='meetingid',
            field=models.TextField(max_length=512),
        ),
        migrations.AlterField(
            model_name='allmeetinginformation',
            name='organizer',
            field=models.CharField(max_length=254),
        ),
        migrations.AlterField(
            model_name='allmeetinginformation',
            name='subject',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
    ]
