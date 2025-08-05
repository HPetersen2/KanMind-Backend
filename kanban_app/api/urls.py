from django.urls import path
from .views import (
    TaskListCreateAPIView,
    TaskUpdateDestroyAPIView,
    CommentListCreateAPIView,
    BoardListCreateView,
    BoardSingleView,
    EmailCheckViewAPIView,
    TaskAssigneeView,
    TaskReviewerView,
    CommentDeleteAPIView,
)

urlpatterns = [
    # Endpoint for listing all boards or creating a new board
    path('boards/', BoardListCreateView.as_view(), name='boards'),

    # Endpoint to retrieve, update or delete a single board identified by its primary key
    path('boards/<int:pk>/', BoardSingleView.as_view(), name='board-details'),

    # Endpoint to check if an email exists or is valid (usually for user validation)
    path('email-check/', EmailCheckViewAPIView.as_view(), name='email-check'),

    # Endpoint for listing all tasks or creating a new task
    path('tasks/', TaskListCreateAPIView.as_view(), name='tasks'),

    # Endpoint to retrieve, update, or delete a task identified by its primary key
    path('tasks/<int:pk>/', TaskUpdateDestroyAPIView.as_view(), name='task-update-destroy'),

    # Endpoint to list all tasks assigned to the authenticated user
    path('tasks/assigned-to-me/', TaskAssigneeView.as_view(), name='tasks-assigned-to-me'),

    # Endpoint to list all tasks where the authenticated user is a reviewer
    path('tasks/reviewing/', TaskReviewerView.as_view(), name='tasks-reviewing-to-me'),

    # Endpoint for listing all comments or creating a new comment related to a specific task
    path('tasks/<int:task_pk>/comments/', CommentListCreateAPIView.as_view(), name='comments'),

    # Endpoint to delete a specific comment by its primary key, related to a specific task
    path('tasks/<int:task_pk>/comments/<int:pk>/', CommentDeleteAPIView.as_view(), name='comments-delete'),
]