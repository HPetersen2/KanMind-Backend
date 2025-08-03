from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Task, Comment, Board

User = get_user_model()

class UserShortSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class BoardCreateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Board
        fields = ['id', 'title', 'members']


class BoardListSerializer(serializers.ModelSerializer):
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
    reviewer = UserShortSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']
        

class BoardSingleSerializer(serializers.ModelSerializer):
    members_data = UserShortSerializer(source='members', many=True, read_only=True)

    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )

    tasks = TaskShortBoardSerializer(many=True, read_only=True)
    owner_data = UserShortSerializer(source='owner_id', many=False, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'members_data', 'tasks']

class EmailCheckSerializer(serializers.ModelSerializer):
    class Meta:
        Model = User
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    assignee = UserShortSerializer(read_only=True)
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
            'status', 'priority', 'assignee',
            'reviewer',
            'reviewer_id',
            'due_date', 'comments_count'
        ]
        read_only_fields = ['assignee']

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
    