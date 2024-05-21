from django.urls import path
from . import views

urlpatterns = [
    path('baseimagetags/', views.get_base_images)
]
