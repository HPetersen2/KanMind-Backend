from django.db.models import Q, Count
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from .models import Task, Comment, Board
from .serializers import TaskSerializer, UserShortSerializer, CommentSerializer, BoardListSerializer, BoardCreateSerializer, BoardSingleSerializer
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
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).annotate(
            member_count=Count('members', distinct=True),
            ticket_count=Count('tasks', distinct=True),
            tasks_to_do_count=Count('tasks', filter=Q(tasks__status='todo'), distinct=True),
            tasks_high_prio_count=Count('tasks', filter=Q(tasks__priority='high'), distinct=True)
        )

    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        # Set members falls vorhanden
        members = self.request.data.get('members')
        if members:
            board.members.set(members)
        # Optional: Annotate wie bei GET
        board.member_count = board.members.count()
        board.ticket_count = board.tasks.count()
        board.tasks_to_do_count = board.tasks.filter(status='todo').count()
        board.tasks_high_prio_count = board.tasks.filter(priority='high').count()
        self._created_board = board  # Für Response im nächsten Schritt

    def create(self, request, *args, **kwargs):
        """Custom response with full annotated data after POST"""
        response = super().create(request, *args, **kwargs)
        # Nutze den annotierten Board aus perform_create
        serializer = BoardListSerializer(instance=self._created_board)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class BoardSingleView(generics.RetrieveDestroyAPIView):
    queryset = Board.objects.filter()
    serializer_class = BoardSingleSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMember]

class EmailCheckViewAPIView(generics.ListAPIView):
    serializer_class = UserShortSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user

