from django.urls import path
from .views import TaskListView, TaskCreateView

urlpatterns = [
    path('tasks/', TaskListView.as_view(), name='tasks'),
    path('task/create/', TaskCreateView.as_view(), name='task-create'),
]