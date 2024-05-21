# podcast/models.py

from django.db import models

class Podcast(models.Model):
    user_name = models.CharField(max_length=200)
    mp3_file = models.FileField(upload_to='podcasts/')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user_name
