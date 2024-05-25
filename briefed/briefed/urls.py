from django.contrib import admin
from django.urls import path, include
from reels.views import reel_list
from podcast.views import podcast_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reels/', reel_list, name='reel_list'),
    path('podcast/', podcast_view, name='podcast_view'),
    path('accounts/', include('django.contrib.auth.urls')),
]
