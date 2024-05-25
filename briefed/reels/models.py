from django.db import models

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Reel(models.Model):
    # Link each reel to a topic
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    
    # Store date, title, summary, image, sources per reel
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    summary = models.TextField()
    image_url = models.URLField()
    sources = models.JSONField()
    
    def __str__(self):
        return self.title
