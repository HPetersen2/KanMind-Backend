from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    """
    This field creates a one-to-one relationship with the built-in Django User model.
    It ensures that each UserProfile is uniquely linked to one User instance.
    The 'on_delete=models.CASCADE' argument specifies that when the associated User is deleted,
    the UserProfile will be deleted as well, maintaining database integrity.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    """
    This field stores the full name of the user as a character string.
    The maximum length is limited to 255 characters to accommodate long names.
    """
    fullname = models.CharField(max_length=255)

    def __str__(self):
        """This method returns the string representation of the UserProfile instance.
        Here it returns the 'fullname' attribute, which makes it easier to identify
        the UserProfile object when working with Django admin or debugging."""
        return self.fullname