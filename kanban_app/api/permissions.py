from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAdminUser

class IsOwnerOrMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.assignee