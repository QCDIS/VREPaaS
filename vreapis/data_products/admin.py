from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.contrib.gis.forms.widgets import OSMWidget

from . import models


class GeoDataProductAdmin(GISModelAdmin):
    gis_widget = OSMWidget
    gis_widget_kwargs = {
        'attrs': {
            'default_lat': 50,
            'default_lon': 10,
            'default_zoom': 3.5,
            },
        }


admin.site.register(models.DataProduct)
admin.site.register(models.GeoDataProduct, GeoDataProductAdmin)
