"""URLs de l'application detection."""
from django.urls import path
from . import views

app_name = 'detection'

urlpatterns = [
    path('', views.detection_view, name='index'),
    path('api/analyze/', views.api_analyze, name='api_analyze'),
]
