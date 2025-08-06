import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

"""Dynamically get the User model defined in the project settings."""
User = get_user_model()

class Board(models.Model):
    """Represents a board entity, such as a project or workspace."""

    """Title of the board, stored as a string with max length 255 characters."""
    title = models.CharField(max_length=255)

    """Owner of the board, linked to the User model with a foreign key.
    If the owner is deleted, the board is deleted as well (CASCADE).
    The related_name 'owned_boards' allows reverse querying: user.owned_boards."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')

    """Members of the board, represented as a many-to-many relationship to Users.
    This allows multiple users to be members of the same board.
    The related_name 'members' allows reverse querying: user.members."""
    members = models.ManyToManyField(User, related_name='members')

    def __str__(self):
        """Returns the title of the board when converted to a string,
        useful for admin display and debugging."""
        return self.title

class Task(models.Model):
    """Represents a task assigned to a board, with details and status."""

    """Possible status values for a task, with human-readable labels."""
    STATUS_CHOICES = [
        ('to-do', 'To Do'),
        ('in-progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done')
    ]

    """Possible priority levels for a task."""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    """The board to which this task belongs.
    If the board is deleted, its tasks are deleted as well.
    The related_name 'tasks' allows reverse lookup: board.tasks."""
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')

    """Title of the task, limited to 255 characters."""
    title = models.CharField(max_length=255)

    """Description or details about the task."""
    description = models.CharField(max_length=255)

    """Status field indicating the current state of the task."""
    """Must be one of the predefined STATUS_CHOICES."""
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    """Priority field indicating the importance of the task."""
    """Must be one of the PRIORITY_CHOICES."""
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)

    """Due date of the task, defaulting to the current date if not specified."""
    due_date = models.DateField(null=False, default=datetime.date.today)

    """User assigned to complete the task."""
    """The related_name 'assigned_tasks' allows reverse lookup: user.assigned_tasks."""
    assignee = models.ForeignKey(User, related_name='assigned_tasks', on_delete=models.CASCADE)

    """Users assigned as reviewers of the task."""
    """Many-to-many relationship, can be empty (blank=True)."""
    """The related_name 'reviewer' allows reverse lookup: user.reviewer."""
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_tasks")

    def __str__(self):
        """Returns the task title as the string representation."""
        return self.title

class Comment(models.Model):
    """Represents a comment made by a user on a task."""

    """Timestamp of when the comment was created."""
    """Automatically set when the comment is created."""
    created_at = models.DateTimeField(null=False, auto_now_add=True)

    """Author of the comment, linked to the User model."""
    """If the user is deleted, the comment is deleted as well."""
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    """Text content of the comment, limited to 255 characters."""
    content = models.CharField(max_length=255)

    """The task to which this comment belongs."""
    """Related name 'comments' enables reverse lookup: task.comments."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        """Returns the content of the comment as its string representation."""
        return self.content