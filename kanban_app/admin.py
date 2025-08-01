from django.contrib import admin
from kanban_app.api.models import Task, Board

admin.site.register(Task)
admin.site.register(Board)
