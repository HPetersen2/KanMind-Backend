from django.db.models import Q, Count, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from .models import Task, Comment, Board, User
from .serializers import (
    TaskSerializer,
    TaskUpdateDestroySerializer,
    CommentSerializer,
    BoardListSerializer,
    BoardCreateSerializer,
    BoardSingleSerializer,
    BoardUpdateSerializer,
    UserShortSerializer,
    EmailQuerySerializer,
)
from .permissions import IsOwnerOrMember, IsOwner, IsBoardMember, IsCommentBoardMember, IsCommentCreator

class BoardListCreateView(generics.ListCreateAPIView):
    """
    API view to list all Boards accessible to the authenticated user or create a new Board.
    - GET: Returns all Boards where the user is the owner or a member, including annotated counts.
    - POST: Creates a new Board with the authenticated user as the owner and optional members.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Use different serializers for GET (listing) and POST (creation)"""
        if self.request.method == 'POST':
            return BoardCreateSerializer
        return BoardListSerializer

    def get_queryset(self):
        user = self.request.user
        """Query Boards where user is owner or member and annotate with counts for dashboard stats"""
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)
        ).annotate(
            member_count=Count('members', distinct=True),
            ticket_count=Count('tasks', distinct=True),
            tasks_to_do_count=Count('tasks', filter=Q(tasks__status='to-do'), distinct=True),
            tasks_high_prio_count=Count('tasks', filter=Q(tasks__priority='high'), distinct=True)
        )

    def perform_create(self, serializer):
        """Save the new Board instance with the current user as owner"""
        board = serializer.save(owner=self.request.user)

        """Assign members if provided in request data"""
        members = self.request.data.get('members')
        if members:
            board.members.set(members)

        """Manually annotate counts for the created board instance to provide detailed response"""
        board.member_count = board.members.count()
        board.ticket_count = board.tasks.count()
        board.tasks_to_do_count = board.tasks.filter(status='to-do').count()
        board.tasks_high_prio_count = board.tasks.filter(priority='high').count()

        """Store created board for use in response"""
        self._created_board = board

    def create(self, request, *args, **kwargs):
        """
        Overrides default create to return the serialized data of the newly created board,
        including the annotated counts.
        """
        response = super().create(request, *args, **kwargs)
        serializer = BoardListSerializer(instance=self._created_board)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class BoardSingleView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific Board instance by its primary key.
    Permissions:
      - DELETE allowed only for the Board owner.
      - Other methods allowed for owner or members.
    Supports:
      - GET: Returns detailed board info including related tasks (with comment counts) and members.
      - PATCH: Allows partial update with a dedicated update serializer.
    """
    queryset = Board.objects.all()

    def get_queryset(self):
        """Prefetch related tasks with comment counts and related user fields for efficiency"""
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
        """Use a specialized serializer for PATCH updates, else default detailed serializer"""
        if self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return BoardSingleSerializer


class EmailCheckAPIView(APIView):
    """
    API view to check for the existence of a user with a given email.
    Requires authenticated user.
    Query parameter: ?email=<email>
    Returns user data if found, otherwise raises a 404 NotFound.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query_serializer = EmailQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        email = query_serializer.validated_data["email"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise NotFound(detail="A user with this email does not exist.")

        serializer = UserShortSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TaskListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all tasks or create a new task.
    Requires user to be authenticated and to be either the board owner or a member.
    Tasks are annotated with the number of related comments.
    """
    http_method_names = ['post']
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrMember]

    def get_queryset(self):
        return Task.objects.annotate(comments_count=Count('comments'))

    def create(self, request, *args, **kwargs):
        # Standardmäßige Validierung & Speicherung
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        # Re-fetch mit Annotation
        task = (
            Task.objects.annotate(comments_count=Count('comments'))
            .get(pk=task.pk)
        )

        # Response-Serialisierung
        output_serializer = self.get_serializer(task)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)



class TaskUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a Task instance.
    Permissions ensure only the assignee, reviewer, or board owner can perform these actions.
    Validation checks ensure assignee and reviewer belong to the board's members or are the owner.
    """
    http_method_names = ['patch', 'delete']
    serializer_class = TaskUpdateDestroySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsBoardMember
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
                raise ValidationError({'assignee': 'Assignee must be a member of the board.'})

        reviewer = validated_data.get('reviewer')
        if reviewer:
            if reviewer != board.owner and not board.members.filter(pk=reviewer.pk).exists():
                raise ValidationError({'reviewer': 'Reviewer must be a member of the board.'})

        serializer.save()

class TaskAssigneeView(generics.ListAPIView):
    """
    API view to list all tasks assigned to the authenticated user.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            Task.objects
            .filter(assignee=user)
            .annotate(comments_count=Count('comments'))
        )


class TaskReviewerView(generics.ListAPIView):
    """
    API view to list all tasks where the authenticated user is a reviewer.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            Task.objects
            .filter(reviewer=user)
            .annotate(comments_count=Count('comments'))
        )


class CommentListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all comments related to a specific task or create a new comment.
    Permissions allow only board owners or members.
    Comments are ordered by creation date descending.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentBoardMember]
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
    """
    API view to delete a specific comment by its primary key related to a specific task.
    Only the author of the comment is allowed to delete it.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCommentCreator]

    def get_queryset(self):
        task_pk = self.kwargs['task_pk']
        return Comment.objects.filter(task_id=task_pk)