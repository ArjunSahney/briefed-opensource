from django.shortcuts import render
from django.contrib.auth.models import User
from .models import TopicsTable, UserInterests

def user_reels(request, user_id):
    user = User.objects.get(id=user_id)
    interests = UserInterests.objects.filter(user=user).select_related('topic')
    reels = []

    for interest in interests:
        topic = interest.topic
        # Assuming reels are stored in the topic's briefs JSON field
        topic_reels = topic.briefs.get('reels', [])
        reels.extend(topic_reels)

    return render(request, 'user_reels.html', {'user': user, 'reels': reels})