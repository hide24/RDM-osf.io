# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2020-10-07 23:02
from __future__ import unicode_literals

import addons.base.institutions_utils
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import osf.models.base


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('osf', '0001_initial'),
        ('osf', '0080_auto_20180423_0634'),
    ]

    operations = [
        migrations.CreateModel(
            name='NodeSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('_id', models.CharField(db_index=True, default=osf.models.base.generate_object_id, max_length=24, unique=True)),
                ('deleted', models.BooleanField(default=False)),
                ('folder_id', models.TextField(blank=True, null=True)),
                ('addon_option', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addons_s3compatinstitutions_node_settings', to='osf.RdmAddonOption')),
                ('owner', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addons_s3compatinstitutions_node_settings', to='osf.AbstractNode')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, addons.base.institutions_utils.InstitutionsStorageAddon),
        ),
    ]
