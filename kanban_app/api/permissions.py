from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAdminUser
from .models import Board

class IsOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user in obj.members.all()
    
class IsTaskAssigneeOrReviewer(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.assignee or request.user in obj.reviewer.all()
    
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner
    
class IsBoardOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == Board.objects.all().owner