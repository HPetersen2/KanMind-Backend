import os
import django
import datetime
import random
from django.contrib.auth.models import User
from kanban_app.api.models import Board, Task, Comment  # Passe myapp an den App-Namen an

# Setup Django-Umgebung (nur nötig, wenn du NICHT über shell oder custom command läufst)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  # anpassen!
django.setup()

# --- Hilfsfunktionen ---
def create_users():
    users = []
    for i in range(5):
        user, created = User.objects.get_or_create(
            username=f"user{i}",
            defaults={"email": f"user{i}@example.com", "password": "test1234"}
        )
        users.append(user)
    return users

def create_boards(users):
    boards = []
    for i in range(2):
        board = Board.objects.create(title=f"Board {i}", owner=users[i])
        board.members.set(users)  # alle als Mitglieder
        boards.append(board)
    return boards

def create_tasks(boards, users):
    statuses = ['todo', 'in_progress', 'done']
    priorities = ['low', 'medium', 'high']
    for board in boards:
        for i in range(5):
            Task.objects.create(
                board=board,
                title=f"Task {i} on {board.title}",
                description="Lorem ipsum dolor sit amet.",
                status=random.choice(statuses),
                priority=random.choice(priorities),
                due_date=datetime.date.today() + datetime.timedelta(days=random.randint(1, 30)),
                assignee=random.choice(users),
                reviewer=random.choice(User)
            )

def create_comments(users):
    tasks = Task.objects.all()
    for task in tasks:
        for i in range(2):
            Comment.objects.create(
                author=random.choice(users),
                content=f"Comment {i} on {task.title}",
                task=task  # Hier fehlt im Model der Bezug Task!
            )

# --- Ausführung ---
users = create_users()
boards = create_boards(users)
create_tasks(boards, users)
#create_comments(users)  # Optional, siehe Hinweis unten

print("Testdaten wurden erfolgreich erstellt.")
