# -*- coding: utf-8 -*-

from django.db import models
from osf.models.base import BaseModel, ObjectIDMixin

class RdmWorkflows(ObjectIDMixin, BaseModel):

    workflow_description = models.CharField(max_length=255, unique=True)
    workflow_apps = models.CharField(max_length=255, unique=True)

class RdmWebMeetingApps(ObjectIDMixin, BaseModel):

    app_name = models.CharField(max_length=255, unique=True)
