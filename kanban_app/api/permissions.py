from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Board

class IsOwnerOrMember(BasePermission):
    # Permission to allow access if the user is the owner or a member of the Board object.
    def has_object_permission(self, request, view, obj):
        # Return True if the requesting user is the owner or is included in the board members.
        return request.user == obj.owner or request.user in obj.members.all()
    
class IsTaskAssigneeOrReviewer(BasePermission):
    # Permission that grants access if the user is either the assignee or one of the reviewers of a Task.
    def has_object_permission(self, request, view, obj):
        # Return True if the requesting user is the task assignee or is in the reviewers list.
        return request.user == obj.assignee or request.user in obj.reviewer.all()
    
class IsOwner(BasePermission):
    # Permission to restrict access only to the owner of the object.
    def has_object_permission(self, request, view, obj):
        # Return True if the requesting user is the owner.
        return request.user == obj.owner
    
class IsBoardMember(BasePermission):
    """
    Permission allowing only Board owners or members to create tasks.
    """
    def has_permission(self, request, view):
        # Extract the 'board' field from the incoming POST data.
        board_id = request.data.get('board')
        if not board_id:
            # Deny permission if no board is specified.
            return False
        try:
            # Attempt to retrieve the Board instance by its primary key.
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            # Deny permission if the Board does not exist.
            return False

        # Grant permission if the user is the board owner or a member of the board.
        return request.user == board.owner or request.user in board.members.all()

class IsTaskAssigneeOrReviewerOrBoardOwnerForDelete(BasePermission):
    """
    Combined permission logic for Task objects:
    - For safe methods (GET) and updates (PUT, PATCH): allow if user is assignee or reviewer.
    - For DELETE method: allow if user is assignee or the owner of the board to which the task belongs.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in SAFE_METHODS or request.method in ['PUT', 'PATCH']:
            # Allow if user is task assignee or a reviewer for read or update operations.
            return user == obj.assignee or user in obj.reviewer.all()

        if request.method == 'DELETE':
            # Allow delete if user is task assignee or the owner of the associated board.
            return user == obj.assignee or user == obj.board.owner

        # Deny permission for all other cases.
        return False

class IsBoardOwner(BasePermission):
    """
    Permission that allows only the Board owner to delete the board.
    """
    def has_object_permission(self, request, view, obj):
        # Return True only if the user is the owner of the board.
        return request.user == obj.owner
    
class IsCommentCreator(BasePermission):
    # Permission to allow only the creator (author) of a comment to access it.
    def has_object_permission(self, request, view, obj):
        # Return True if the user is the author of the comment.
        return request.user == obj.author