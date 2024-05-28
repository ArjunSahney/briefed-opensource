from django.contrib import admin
from django.urls import path, include
from reels.views import user_reels
from podcast.views import podcast_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reels/', user_reels, name='reel_list'),
    path('podcast/', podcast_view, name='podcast_view'),
    path('accounts/', include('django.contrib.auth.urls')),
]
