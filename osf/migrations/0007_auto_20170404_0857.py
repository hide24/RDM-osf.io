# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-04-04 13:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0006_add_jsonb_index_for_fileversions'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='preprintservice',
            options={'permissions': (('view_preprintservice', 'Can view preprint service details in the admin app.'),)},
        ),
    ]
