# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2021-05-25 11:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('addons_integromat', '0014_auto_20210524_1117'),
    ]

    operations = [
        migrations.CreateModel(
            name='AllMeetingInformationAttendeesRelation',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('webex_meetings_invitee_id', models.CharField(blank=True, max_length=128, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='allmeetinginformation',
            name='attendees',
            field=models.ManyToManyField(related_name='attendees_meetings', to='addons_integromat.Attendees'),
        ),
        migrations.AddField(
            model_name='allmeetinginformationattendeesrelation',
            name='allMeetingInformation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='addons_integromat.AllMeetingInformation'),
        ),
        migrations.AddField(
            model_name='allmeetinginformationattendeesrelation',
            name='attendees',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='addons_integromat.Attendees'),
        ),
        migrations.AddField(
            model_name='allmeetinginformation',
            name='attendees_specific',
            field=models.ManyToManyField(related_name='attendees_specific_meetings', through='addons_integromat.AllMeetingInformationAttendeesRelation', to='addons_integromat.Attendees'),
        ),
    ]
