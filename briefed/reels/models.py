from django.db import models

class TopicsTable(models.Model):
    date = models.DateField()
    datetime = models.DateTimeField()
    briefs = models.JSONField()

    # class Meta:
    #     indexes = [
    #         models.Index(fields=['briefs'], name='topics_table_briefs_index'),
    #     ]

class UserTable(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    password = models.CharField(max_length=255)

class UserInterests(models.Model):
    topic = models.ForeignKey(TopicsTable, on_delete=models.CASCADE)
    user = models.ForeignKey(UserTable, on_delete=models.CASCADE)
    topic_name = models.CharField(max_length=255)

class Podcasts(models.Model):
    user = models.ForeignKey(UserTable, on_delete=models.CASCADE)
    date = models.DateField()
