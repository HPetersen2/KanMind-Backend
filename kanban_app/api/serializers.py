from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Task, Comment, Board

User = get_user_model()

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']

class TaskSerializer(serializers.ModelSerializer):
    assignee = UserShortSerializer(read_only=True)
    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description',
            'status', 'priority', 'due_date', 'assignee'
        ]
        read_only_fields = ['assignee']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
    

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
        