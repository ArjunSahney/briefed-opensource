from django.urls import path
from .views import GenerateTopBriefsView, GenerateCustomBriefsView, CreatePodcastView

urlpatterns = [
    path('generate-top-briefs/', GenerateTopBriefsView.as_view(), name='generate_top_briefs'),
    path('generate-custom-briefs/', GenerateCustomBriefsView.as_view(), name='generate_custom_briefs'),
    path('create-podcast/', CreatePodcastView.as_view(), name='create_podcast'),
]