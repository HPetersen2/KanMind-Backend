from django.db import models

class Task(models.Model):
    board = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    priority = models.CharField(max_length=255)


class Board(models.Model):
    title = models.CharField(max_length=255)
    member_count = models.IntegerField()
    ticket_count = models.IntegerField()
    tasks_to_do_count = models.IntegerField()
    tasks_high_prio_count = models.IntegerField()
    owner_id = models.IntegerField()

    def __str__(self):
        self.title
