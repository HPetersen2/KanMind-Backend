from django.urls import path
from .views import TaskListCreateAPIView, TaskUpdateDestroyAPIView, CommentListCreateAPIView,  BoardListCreateAPIView, EmailCheckViewAPIView

urlpatterns = [
    path('tasks/', TaskListCreateAPIView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', TaskUpdateDestroyAPIView.as_view(), name='task-update-destroy'),
    path('boards/', BoardListCreateAPIView.as_view(), name='boards'),
    path('email-check', EmailCheckViewAPIView.as_view(), name='email-check'),
    path('tasks/comments/', CommentListCreateAPIView.as_view(), name='comments'),
]