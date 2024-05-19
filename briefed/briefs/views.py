from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Brief, UserInterest, Podcast
from django.contrib.auth.models import User
from .your_script import generate_top_briefs, generate_custom, create_podcast

class GenerateCustomBriefsView(APIView):
    def post(self, request):
        user = request.user
        interests = request.data.get("interests", [])
        for interest in interests:
            UserInterest.objects.get_or_create(user=user, interest=interest)
        custom_briefs = generate_custom(user, interests)
        custom_briefs_data = [
            {'title': brief.title, 'content': brief.content, 'interest': brief.interest, 'sources': json.loads(brief.sources)}
            for brief in custom_briefs
        ]
        return Response({"status": "Custom briefs generated", "briefs": custom_briefs_data})