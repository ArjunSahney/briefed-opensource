from django.shortcuts import render
from .models import Podcast
from django.contrib.auth.decorators import login_required

@login_required
def podcast_view(request):
    user = request.user
    podcast = Podcast.objects.filter(user_name=user.username).first()
    return render(request, 'podcast/podcast_view.html', {'podcast': podcast})
