from django.urls import path
from . import views

urlpatterns = [
    path('', views.reel_feed, name='reel_feed'),
]
