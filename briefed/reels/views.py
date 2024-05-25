from django.shortcuts import render
from .models import Reel
from django.contrib.auth.decorators import login_required

@login_required
def reel_list(request):
    user = request.user
    reels = Reel.objects.filter(topic__name=user.username)  # Assuming each topic name is the username
    return render(request, 'reels/reel_list.html', {'reels': reels})
