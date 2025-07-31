from django.db.models import Q, Count
from rest_framework import generics
from rest_framework import permissions
from .models import Task, Comment, Board
from .serializers import TaskSerializer, UserShortSerializer, CommentSerializer, BoardListSerializer, BoardCreateSerializer
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

class BoardListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BoardCreateSerializer
        return BoardListSerializer

    def get_queryset(self):
        return Board.objects.annotate(
            member_count=Count('members', distinct=True),
            ticket_count=Count('tasks', distinct=True),
            tasks_to_do_count=Count('tasks', filter=Q(tasks__status='todo'), distinct=True),
            tasks_high_prio_count=Count('tasks', filter=Q(tasks__priority='high'), distinct=True)
        )

    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        board.members.add(self.request.user)  # Optional: Owner als Member hinzufügen
    
class EmailCheckViewAPIView(generics.ListAPIView):
    serializer_class = UserShortSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user

