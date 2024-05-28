from django.urls import path
from .views import user_reels

urlpatterns = [
    path('user/<int:user_id>/reels/', user_reels, name='user_reels'),
]
