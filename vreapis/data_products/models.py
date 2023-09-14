from django.db import models
from django.contrib.gis.db import models as gis_models


from virtual_labs.models import VirtualLab
from workflows.models import Workflow


class DataProduct(models.Model):
    uuid = models.UUIDField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True)

    vlab = models.ForeignKey(VirtualLab, on_delete=models.DO_NOTHING, null=True)
    workflow = models.ForeignKey(Workflow, on_delete=models.DO_NOTHING,
                                 null=True, blank=True)
    data_url = models.URLField(null=True)


class GeoDataProduct(DataProduct, gis_models.Model):
    spatial_coverage = gis_models.MultiPolygonField()
    raster_data_url = models.URLField(null=True)
