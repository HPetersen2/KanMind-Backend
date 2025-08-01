from django.urls import path
from .views import TaskListCreateAPIView, TaskUpdateDestroyAPIView, CommentListCreateAPIView,  BoardListCreateView, BoardSingleView, EmailCheckViewAPIView

urlpatterns = [
    path('tasks/', TaskListCreateAPIView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', TaskUpdateDestroyAPIView.as_view(), name='task-update-destroy'),
    path('boards/', BoardListCreateView.as_view(), name='boards'),
    path('boards/<int:pk>/', BoardSingleView.as_view(), name='board-details'),
    path('email-check', EmailCheckViewAPIView.as_view(), name='email-check'),
    path('tasks/comments/', CommentListCreateAPIView.as_view(), name='comments'),
]