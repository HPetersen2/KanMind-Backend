from django.urls import path
from .views import TaskListCreateAPIView, TaskUpdateDestroyAPIView, BoardListCreateAPIView

urlpatterns = [
    path('tasks/', TaskListCreateAPIView.as_view(), name='tasks'),
    path('task/<int:pk>/', TaskUpdateDestroyAPIView.as_view(), name='task-update-destroy'),
    path('boards/', BoardListCreateAPIView.as_view(), name='boards'),
]