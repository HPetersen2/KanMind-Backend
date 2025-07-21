from django.db import models

class Task(models.Model):
    board = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    priority = models.CharField(max_length=255)
