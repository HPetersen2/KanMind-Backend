from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Task, Comment, Board

User = get_user_model()

class UserShortSerializer(serializers.ModelSerializer):
    # Serializer for a concise representation of a User,
    # including a computed full name field.
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
    
    def get_fullname(self, obj):
        return obj.userprofile.fullname
        

class BoardCreateSerializer(serializers.ModelSerializer):
    # Serializer for creating a Board, accepting member IDs.
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Board
        fields = ['id', 'title', 'members']

class BoardListSerializer(serializers.ModelSerializer):
    # Serializer for listing Board objects with additional counts.
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
    # Short serializer for Task embedded within Board representations,
    # includes reviewer details and comment count.
    reviewer = UserShortSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 
            'status', 'priority', 'assignee',
            'reviewer', 'due_date', 'comments_count'
        ]

class BoardSingleSerializer(serializers.ModelSerializer):
    # Detailed Board serializer including members and tasks with nested serializers.
    members = UserShortSerializer(many=True, read_only=True)
    tasks = TaskShortBoardSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']

class BoardUpdateSerializer(serializers.ModelSerializer):
    # Serializer for updating Board, accepts member IDs as input,
    # returns full member and owner info as read-only nested data.
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
        # Custom update method to handle members field separately.
        members = validated_data.pop('members', None)

        # Update other fields on the instance.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # If members were provided, update the many-to-many relationship.
        if members is not None:
            instance.members.set(members)

        return instance

class EmailQuerySerializer(serializers.Serializer):
    # Simple serializer to validate a single email field.
    email = serializers.EmailField(required=True)

class TaskSerializer(serializers.ModelSerializer):
    # Serializer for Task with nested short user representations and
    # separate write-only fields for setting assignee and reviewers by ID.
    assignee = UserShortSerializer(read_only=True)  # Read-only for responses.
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False
    )
    reviewer = UserShortSerializer(many=True, read_only=True)
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        many=True,
        write_only=True
    )
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description',
            'status', 'priority',
            'assignee', 'assignee_id',
            'reviewer', 'reviewer_id',
            'due_date', 'comments_count'
        ]
        read_only_fields = ['assignee']

class CommentSerializer(serializers.ModelSerializer):
    # Serializer for Comment with author set to the authenticated user automatically.
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']

    def create(self, validated_data):
        # Override to automatically set the author from the request user.
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)