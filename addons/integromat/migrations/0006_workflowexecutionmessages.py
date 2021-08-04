# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2021-02-18 08:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('addons_integromat', '0005_auto_20210115_1038'),
    ]

    operations = [
        migrations.CreateModel(
            name='workflowExecutionMessages',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('create_microsoft_teams_meeting', models.CharField(blank=True, max_length=128, null=True)),
                ('update_microsoft_teams_meeting', models.CharField(blank=True, max_length=128, null=True)),
                ('delete_microsoft_teams_meeting', models.CharField(blank=True, max_length=128, null=True)),
                ('node_settings', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='addons_integromat.NodeSettings')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
