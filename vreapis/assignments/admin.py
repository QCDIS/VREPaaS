from django.contrib import admin
from assignments.models import Assignment
from django.forms import TextInput, Textarea
from django.db import models


class MyAssignmentAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(MyAssignmentAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['long_description'].widget.attrs['style'] = 'width: 45em;height: 25em;'
        return form

admin.site.register(Assignment,MyAssignmentAdmin)
# admin.site.register(KeyCloakAuth)