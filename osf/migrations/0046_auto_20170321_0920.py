# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-03-21 14:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0045_auto_20170320_1819'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='basefilenode',
            unique_together=set([('node', 'name', 'parent', 'type', '_path')]),
        ),
    ]
