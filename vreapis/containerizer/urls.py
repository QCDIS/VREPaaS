from django.urls import path
from . import views

urlpatterns = [
    path('baseimagetags', views.get_base_images),
    path('extract', views.ExtractorHandler.as_view()),
    path('types', views.TypesHandler.as_view()),
    path('baseimage', views.BaseImageHandler.as_view()),
    path('addcell', views.CellsHandler.as_view()),
]
