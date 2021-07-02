# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2021-06-10 03:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('addons_integromat', '0017_auto_20210528_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allmeetinginformation',
            name='end_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='allmeetinginformation',
            name='start_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='allmeetinginformation',
            name='subject',
            field=models.CharField(default='my meeting', max_length=254),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='workflowexecutionmessages',
            name='integromat_msg',
            field=models.CharField(default='msg', max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='workflowexecutionmessages',
            name='timestamp',
            field=models.CharField(default='0000000000000', max_length=128),
            preserve_default=False,
        ),
    ]
