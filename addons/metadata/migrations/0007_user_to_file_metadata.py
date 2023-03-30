# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2023-01-13 09:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import osf.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('addons_metadata', '0006_add_japan_grant_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='filemetadata',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='file_metadata_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='filemetadata',
            name='deleted',
            field=osf.utils.fields.NonNaiveDateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='filemetadata',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='file_metadata_modified', to=settings.AUTH_USER_MODEL),
        ),
    ]