"""vreapis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from virtual_labs.views import VirtualLabViewSet
from cells.views import CellsViewSet
from workflows.views import WorkflowViewSet
from data_products.views import DataProductsViewSet, GeoDataProductsViewSet
from paas_configuration.views import PaasConfigurationViewSet

from vreapis.settings.base import BASE_PATH



from vreapis.settings.base import BASE_PATH

admin.site.site_header = 'Virtual Labs Administration'

router = routers.DefaultRouter()
router.register(r'vlabs', VirtualLabViewSet)
router.register(r'workflows', WorkflowViewSet)
router.register(r'cells', CellsViewSet)
router.register(r'dataprods', DataProductsViewSet)
router.register(r'geodataprods', GeoDataProductsViewSet)
router.register(r'paas_configuration', PaasConfigurationViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls))
]

if BASE_PATH:
    urlpatterns = [path(f'{BASE_PATH}/', include(urlpatterns))]
