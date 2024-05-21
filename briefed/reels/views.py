from django.shortcuts import render
from .models import Reel

def reel_feed(request):
    reels = Reel.objects.all()  # Retrieve all reels from the database
    return render(request, 'reels/feed.html', {'reels': reels})

