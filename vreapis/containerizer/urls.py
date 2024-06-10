from django.urls import path
from . import views

urlpatterns = [
    path('baseimagetags/', views.get_base_images),
    path('extractorhandler/', views.ExtractorHandler.as_view()),
    path('cellshandler/', views.CellsHandler.as_view()),
]
