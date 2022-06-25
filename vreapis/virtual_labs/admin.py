from django.contrib import admin

from virtual_labs.models import VM, KeyCloakAuth, SDIAProvision, Topology, VLProfile, VirtualLab, TokenCredentials

admin.site.register(VirtualLab)
admin.site.register(TokenCredentials)
# admin.site.register(VLProfile)
# admin.site.register(VM)
# admin.site.register(Topology)
# admin.site.register(SDIAProvision)
# admin.site.register(KeyCloakAuth)
