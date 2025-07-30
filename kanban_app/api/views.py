from django.db.models import Q
from rest_framework import generics
from rest_framework import permissions
from .models import Task, Comment, Board
from .serializers import TaskSerializer, UserShortSerializer, CommentSerializer, BoardSerializer
from .permissions import IsOwnerOrMember


class TaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(assignee=self.request.user)

class TaskUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMember]

class CommentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class BoardListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permissions_class = [permissions.IsAuthenticated, IsOwnerOrMember]
    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
    
class EmailCheckViewAPIView(generics.ListAPIView):
    serializer_class = UserShortSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user

