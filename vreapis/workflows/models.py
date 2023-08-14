from django.db import models
from virtual_labs.models import VirtualLab

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings


class Workflow(models.Model):
    created = models.DateTimeField(auto_now_add=True, null=True)
    argo_id = models.CharField(primary_key=True, max_length=100)
    vlab = models.ForeignKey(VirtualLab, on_delete=models.DO_NOTHING, null=True)
    status = models.CharField(max_length=50, null=True)
    progress = models.CharField(max_length=50, null=True)
    argo_url = models.URLField(null=True)
