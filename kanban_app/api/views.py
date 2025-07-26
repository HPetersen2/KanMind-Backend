from django.db.models import Q
from rest_framework import generics, mixins
from rest_framework import permissions
from .models import Task, Board
from .serializers import TaskSerializer, BoardSerializer
from .permissions import IsOwnerOrMember

class TaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TaskUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class BoardListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    permissions_class = [permissions.IsAuthenticated, IsOwnerOrMember]
    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()