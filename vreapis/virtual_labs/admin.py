from django.contrib import admin
from virtual_labs.models import VirtualLab, VirtualLabInstance

admin.site.register(VirtualLab)
admin.site.register(VirtualLabInstance)
