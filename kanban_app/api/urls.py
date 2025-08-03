from django.urls import path
from .views import TaskListCreateAPIView, TaskUpdateDestroyAPIView, CommentListCreateAPIView,  BoardListCreateView, BoardSingleView, EmailCheckViewAPIView, TaskOwnView, TaskReviewerView

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='boards'),
    path('boards/<int:pk>/', BoardSingleView.as_view(), name='board-details'),
    path('email-check/', EmailCheckViewAPIView.as_view(), name='email-check'),
    path('tasks/', TaskListCreateAPIView.as_view(), name='tasks'),
    path('tasks/<int:pk>/', TaskUpdateDestroyAPIView.as_view(), name='task-update-destroy'),
    path('tasks/assigned-to-me/', TaskOwnView.as_view(), name='tasks-assigned-to-me'),
    path('tasks/reviewing/', TaskReviewerView.as_view(), name='tasks-reviewing-to-me'),
    path('tasks/<int:pk>/comments/', CommentListCreateAPIView.as_view(), name='comments'),
]