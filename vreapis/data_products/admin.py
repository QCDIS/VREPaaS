from django.contrib import admin
from . import models

admin.site.register(models.DataProduct)
admin.site.register(models.GeoDataProduct)
