from django.db import models

class Reel(models.Model):
    topic = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    summary = models.TextField()
    image_url = models.URLField()
    sources = models.JSONField()
    
    def __str__(self):
        return self.title
