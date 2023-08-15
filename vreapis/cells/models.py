from django.db import models
from virtual_labs.models import VirtualLab
from assignments.models import Assignment

class Catalog(models.Model):

    name = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    vlab = models.ForeignKey(VirtualLab, on_delete=models.DO_NOTHING, null=True)
    ass = models.ForeignKey(Assignment, on_delete=models.DO_NOTHING, null=True)
    def __str__(self):
        return self.name
    

class Cell(models.Model):

    uuid = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    container_image = models.CharField(max_length=100, null=True)
    registry_url = models.URLField(null=True)
    repository_url = models.URLField(null=True)
    cell_metadata = models.JSONField(null=True)
    catalog = models.ForeignKey(Catalog, on_delete=models.DO_NOTHING, null=True)

    def __str__(self) -> str:
        return self.name