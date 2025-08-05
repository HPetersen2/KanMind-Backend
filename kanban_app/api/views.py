from django.db.models import Q, Count, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework import filters
from .models import Task, Comment, Board, User
from .serializers import TaskSerializer, CommentSerializer, BoardListSerializer, BoardCreateSerializer, BoardSingleSerializer, BoardUpdateSerializer, UserShortSerializer, EmailQuerySerializer
from .permissions import IsOwnerOrMember, IsOwner, IsBoardMember, IsTaskAssigneeOrReviewerOrBoardOwnerForDelete, IsCommentCreator

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
            tasks_to_do_count=Count('tasks', filter=Q(tasks__status='to-do'), distinct=True),
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
    queryset = Board.objects.all()

    def get_queryset(self):
        return Board.objects.prefetch_related(
            Prefetch(
                'tasks',
                queryset=Task.objects.annotate(
                    comments_count=Count('comments')
                ).prefetch_related('reviewer', 'assignee')
            ),
            'members'
        ).select_related('owner')

    def get_permissions(self):
        if self.request.method == 'DELETE':
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrMember]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return BoardSingleSerializer


class EmailCheckViewAPIView(generics.ListAPIView):
    serializer_class = UserShortSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query_serializer = EmailQuerySerializer(data=self.request.query_params)
        query_serializer.is_valid(raise_exception=True)
        email = query_serializer.validated_data['email']

        queryset = User.objects.filter(email__iexact=email)

        if not queryset.exists():
            raise NotFound(detail="Ein Benutzer mit dieser E-Mail existiert nicht.")

        return queryset

class TaskListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsBoardMember]

    def get_queryset(self):
        return Task.objects.annotate(comments_count=Count('comments'))
    
    def perform_create(self, serializer):
        serializer.save()

class TaskUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsTaskAssigneeOrReviewerOrBoardOwnerForDelete
    ]

    def get_queryset(self):
        return Task.objects.annotate(comments_count=Count('comments'))

    def perform_update(self, serializer):
        task = self.get_object()
        board = task.board
        validated_data = serializer.validated_data

        assignee = validated_data.get('assignee')
        if assignee:
            if assignee != board.owner and not board.members.filter(pk=assignee.pk).exists():
                raise ValidationError({'assignee': 'Assignee muss Mitglied des Boards sein.'})

        reviewers = validated_data.get('reviewer')
        if reviewers:
            invalid_users = []
            for reviewer in reviewers:
                if reviewer != board.owner and not board.members.filter(pk=reviewer.pk).exists():
                    invalid_users.append(reviewer.pk)

            if invalid_users:
                raise ValidationError({
                    'reviewer': f'Folgende Reviewer sind keine Mitglieder des Boards: {invalid_users}'
                })

        serializer.save()
    

class TaskAssigneeView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(Q(assignee=user))

class TaskReviewerView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(Q(reviewer=user))

class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMember]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        task_pk = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_pk)
        return Comment.objects.filter(task=task)

    def perform_create(self, serializer):
        task_pk = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, pk=task_pk)
        serializer.save(author=self.request.user, task=task)

class CommentDeleteAPIView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentCreator]

    def get_queryset(self):
        task_pk = self.kwargs['task_pk']
        return Comment.objects.filter(task_id=task_pk)

