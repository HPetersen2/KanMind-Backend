from django.db import models

class UserProfile(models.Model):
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    user_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.firstName} {self.lastName} ({self.email})"