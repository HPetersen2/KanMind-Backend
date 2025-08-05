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
    path('boards/', BoardListCreateView.as_view(), name='boards'),
    path('boards/<int:pk>/', BoardSingleView.as_view(), name='board-details'),
    path('email-check/', EmailCheckViewAPIView.as_view(), name='email-check'),
    path('tasks/', TaskListCreateAPIView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', TaskUpdateDestroyAPIView.as_view(), name='task-update-destroy'),
    path('tasks/assigned-to-me/', TaskAssigneeView.as_view(), name='tasks-assigned-to-me'),
    path('tasks/reviewing/', TaskReviewerView.as_view(), name='tasks-reviewing-to-me'),
    path('tasks/<int:task_pk>/comments/', CommentListCreateAPIView.as_view(), name='comments'),
    path('tasks/<int:task_pk>/comments/<int:pk>/', CommentDeleteAPIView.as_view(), name='comments-delete'),
]