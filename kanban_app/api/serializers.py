from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Task, Comment, Board

User = get_user_model()

class UserShortSerializer(serializers.ModelSerializer):
    """Serializer for a concise representation of a User,
    including a computed full name field."""
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
    def get_fullname(self, obj):
        if hasattr(obj, 'userprofile') and obj.userprofile:
            return obj.userprofile.fullname
        return ''
        

class BoardCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a Board, accepting member IDs."""
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Board
        fields = ['id', 'title', 'members']

class BoardListSerializer(serializers.ModelSerializer):
    """Serializer for listing Board objects with additional counts."""
    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'member_count', 'ticket_count',
            'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id'
        ]

class TaskShortBoardSerializer(serializers.ModelSerializer):
    """Short serializer for Task embedded within Board representations,
    includes reviewer details and comment count."""
    reviewer = UserShortSerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 
            'status', 'priority', 'assignee',
            'reviewer', 'due_date', 'comments_count'
        ]

class BoardSingleSerializer(serializers.ModelSerializer):
    """Detailed Board serializer including members and tasks with nested serializers."""
    members = UserShortSerializer(many=True, read_only=True)
    tasks = TaskShortBoardSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

class BoardUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Board, accepts member IDs as input,
    returns full member and owner info as read-only nested data."""
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )
    members_data = UserShortSerializer(source='members', many=True, read_only=True)
    owner_data = UserShortSerializer(source='owner', read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']

    def update(self, instance, validated_data):
        """Custom update method to handle members field separately."""
        members = validated_data.pop('members', None)

        """Update other fields on the instance."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        """If members were provided, update the many-to-many relationship."""
        if members is not None:
            instance.members.set(members)

        return instance

class EmailQuerySerializer(serializers.Serializer):
    """Simple serializer to validate a single email field."""
    email = serializers.EmailField(required=True)

class CommaSeparatedUserField(serializers.Field):
    """
    Custom field to handle user IDs as a single int, a comma-separated string,
    or a list of ints. Converts them to User instances and validates existence.
    """

    def to_internal_value(self, data):
        """
        Parse input into a list of User objects. Supports:
        - int
        - comma-separated string
        - list of ints
        Raises error if users don't exist.
        """
        if isinstance(data, int):
            data = [data]
        elif isinstance(data, str):
            data = [int(pk.strip()) for pk in data.split(',')]
        elif isinstance(data, list):
            data = [int(pk) for pk in data]
        else:
            raise serializers.ValidationError("Invalid format for reviewer_id")

        users = User.objects.filter(pk__in=data)
        if users.count() != len(data):
            raise serializers.ValidationError("One or more users do not exist.")
        return list(users)

    def to_representation(self, value):
        """
        Return list of user IDs from User instances.
        """
        return [user.pk for user in value]

class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task with nested short user representations and
    separate write-only fields for setting assignee and reviewers by ID."""
    assignee = UserShortSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False
    )
    reviewer = UserShortSerializer(read_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False
    )
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description',
            'status', 'priority',
            'assignee', 'assignee_id',
            'reviewer', 'reviewer_id',  # ← Singular
            'due_date', 'comments_count'
        ]

class TaskUpdateDestroySerializer(serializers.ModelSerializer):
    """Serializer for Task with nested short user representations and
    separate write-only fields for setting assignee and reviewers by ID."""
    assignee = UserShortSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False
    )
    reviewer = UserShortSerializer(read_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='reviewer',
        write_only=True,
        required=False
    )

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description',
            'status', 'priority',
            'assignee', 'assignee_id',
            'reviewer', 'reviewer_id',
            'due_date'
        ]

class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment with author set to the authenticated user automatically."""
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']

    def get_author(self, obj):
        user = obj.author
        if hasattr(user, 'userprofile') and user.userprofile.fullname:
            return user.userprofile.fullname
        return user.username

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)