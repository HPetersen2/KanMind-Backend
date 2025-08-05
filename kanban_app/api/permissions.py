from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.permissions import IsAdminUser
from .models import Board, Task

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
    
class IsBoardMember(BasePermission):
    """
    Nur Board-Owner oder -Mitglieder dürfen Tasks erstellen.
    """
    def has_permission(self, request, view):
        board_id = request.data.get('board')  # board kommt über POST-Daten
        if not board_id:
            return False  # Kein Board angegeben
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            return False

        return request.user == board.owner or request.user in board.members.all()


# 2. Nur Task-Ersteller ODER Board-Ersteller darf Task löschen
class IsTaskAssigneeOrReviewerOrBoardOwnerForDelete(BasePermission):
    """
    Kombinierte Permission:
    - Für GET, PUT, PATCH: erlaubt für Assignee oder Reviewer
    - Für DELETE: erlaubt für Assignee oder Board-Owner
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in SAFE_METHODS or request.method in ['PUT', 'PATCH']:
            return user == obj.assignee or user in obj.reviewer.all()

        if request.method == 'DELETE':
            return user == obj.assignee or user == obj.board.owner

        return False


# 3. Nur Board-Ersteller darf Board löschen
class IsBoardOwner(BasePermission):
    """
    Nur Board-Owner darf ein Board löschen.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner
    
class IsCommentCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.author