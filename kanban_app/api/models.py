from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
class Task(models.Model):
    board = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    priority = models.CharField(max_length=255)


class Board(models.Model):
    title = models.CharField(max_length=255)
    member_count = models.IntegerField(default=0)
    ticket_count = models.IntegerField(default=0)
    tasks_to_do_count = models.IntegerField(default=0)
    tasks_high_prio_count = models.IntegerField(default=0)
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField(User, related_name='member_boards')

    def __str__(self):
        return self.title
