from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from .models import Task, Comment, Board
from .serializers import TaskSerializer, CommentSerializer, BoardListSerializer, BoardCreateSerializer, BoardSingleSerializer, EmailCheckSerializer
from .permissions import IsOwnerOrMember, IsOwner, IsTaskAssigneeOrReviewer

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
    

class BoardSingleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.filter()
    serializer_class = BoardSingleSerializer
    def get_permissions(self):
        if self.request.method == 'DELETE':
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrMember]
        return [permission() for permission in permission_classes]


class EmailCheckViewAPIView(generics.ListAPIView):
    serializer_class = EmailCheckSerializer
    permission_classes = [permissions.IsAuthenticated]

class TaskListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.annotate(comments_count=Count('comments'))

    def perform_create(self, serializer):
        serializer.save(assignee=self.request.user)


class TaskUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskAssigneeOrReviewer]

    def get_queryset(self):
        return Task.objects.annotate(comments_count=Count('comments'))
    

class TaskOwnView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(assignee=user) | Q(reviewer=user)
        )

class TaskReviewerView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(Q(reviewer=user))

class CommentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        task_pk = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_pk)
        serializer.save(author=self.request.user, task=task)

