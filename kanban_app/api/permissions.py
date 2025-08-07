from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import NotFound
from .models import Board, Task

class IsOwnerOrMember(BasePermission):
    """Permission to allow access if the user is the owner or a member of the Board object."""
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True  # Für GET, PATCH, DELETE etc. wird has_object_permission genutzt

        board_id = request.data.get('board')
        if not board_id:
            return False

        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            raise NotFound("Board does not exist.")

        return request.user == board.owner or board.members.filter(pk=request.user.pk).exists()

    
class IsTaskAssigneeOrReviewer(BasePermission):
    """Permission that grants access if the user is either the assignee or one of the reviewer of a Task."""
    def has_object_permission(self, request, view, obj):
        """Return True if the requesting user is the task assignee or is in the reviewer list."""
        return request.user == obj.assignee or request.user == obj.reviewer
    
class IsOwner(BasePermission):
    """Permission to restrict access only to the owner of the object."""
    def has_object_permission(self, request, view, obj):
        """Return True if the requesting user is the owner."""
        return request.user == obj.owner
    
class IsBoardMember(BasePermission):
    """
    Permission allowing only Board owners or members to create tasks.
    """
    def has_object_permission(self, request, view, obj):
        board = obj.board
        user = request.user
        return user == board.owner or board.members.filter(pk=user.pk).exists()

class IsTaskAssigneeOrReviewerOrBoardOwnerForDelete(BasePermission):
    """
    Combined permission logic for Task objects:
    - For safe methods (GET) and updates (PUT, PATCH): allow if user is assignee or reviewer.
    - For DELETE method: allow if user is assignee or the owner of the board to which the task belongs.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in SAFE_METHODS or request.method in ['PUT', 'PATCH']:
            """Allow if user is task assignee or a reviewer for read or update operations."""
            return user == obj.assignee or user == obj.reviewer

        if request.method == 'DELETE':
            """Allow delete if user is task assignee or the owner of the associated board."""
            return user == obj.assignee or user == obj.board.owner

        """Deny permission for all other cases."""
        return False

class IsBoardOwner(BasePermission):
    """
    Permission that allows only the Board owner to delete the board.
    """
    def has_object_permission(self, request, view, obj):
        """Return True only if the user is the owner of the board."""
        return request.user == obj.owner
    
class IsCommentBoardMember(BasePermission):
    """
    Permission that allows only members of the task's board to access.
    Assumes `view.task` is set.
    """

    def has_permission(self, request, view):
        task = getattr(view, 'task', None)
        if not task:
            return False

        board = task.board

        return (
            request.user == board.owner
            or board.members.filter(id=request.user.id).exists()
        )
    
class IsCommentCreator(BasePermission):
    """Permission to allow only the creator (author) of a comment to access it."""
    def has_object_permission(self, request, view, obj):
        """Return True if the user is the author of the comment."""
        return request.user == obj.author
    
class BoardMemberForBoard(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user in obj.members.all()