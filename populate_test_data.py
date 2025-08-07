import os
import django
import datetime
import random

from django.contrib.auth import get_user_model

User = get_user_model()

def create_guest_user():
    email = "guest@kanmind.de"
    user, created = User.objects.get_or_create(
        email=email,
        defaults={"username": "guest"}
    )
    if created:
        user.set_password("guestpassword")
        user.save()
        print(f"Guest user created: {email}")
    else:
        print(f"Guest user exists: {email}")
    return user

def create_boards(owner):
    titles = [
        "NextGen WebApp Development",
        "Mobile App Refactoring",
        "API Enhancement Sprint"
    ]
    boards = []
    for title in titles:
        board, created = Board.objects.get_or_create(title=title, owner=owner)
        board.members.add(owner)
        board.save()
        boards.append(board)
        if created:
            print(f"Board created: {title}")
        else:
            print(f"Board exists: {title}")
    return boards

def create_tasks(boards, user):
    statuses = ['to-do', 'in-progress', 'review', 'done']
    priorities = ['low', 'medium', 'high']

    tasks_data = [
        {
            "board": boards[0],
            "title": "API-Endpunkt für User-Authentifizierung erstellen",
            "description": "Implementiere REST-API-Endpunkt für Login und Token.",
            "status": "to-do",
            "priority": "high",
            "due_date": datetime.date.today() + datetime.timedelta(days=7),
            "assignee": user,
            "reviewer": user,
            "comments": [
                "Muss OAuth 2.0 unterstützen.",
                "Auf Sicherheitslücken achten.",
            ],
        },
        {
            "board": boards[1],
            "title": "Datenbankmodell für Produktkatalog erweitern",
            "description": "Tabellen für Produktvarianten und Lagerbestand hinzufügen.",
            "status": "in-progress",
            "priority": "high",
            "due_date": datetime.date.today() + datetime.timedelta(days=5),
            "assignee": user,
            "reviewer": user,
            "comments": [
                "Indexierung prüfen.",
                "Migration rückwärtskompatibel halten.",
            ],
        },
        {
            "board": boards[2],
            "title": "Dokumentation für Setup-Prozess aktualisieren",
            "description": "Readme um Installationsschritte und Umgebungsvariablen erweitern.",
            "status": "review",
            "priority": "low",
            "due_date": datetime.date.today() + datetime.timedelta(days=8),
            "assignee": user,
            "reviewer": user,
            "comments": [
                "Screenshots für Windows und Mac ergänzen.",
                "Anleitung für Docker-Setup hinzufügen.",
            ],
        },
    ]

    for data in tasks_data:
        task, created = Task.objects.get_or_create(
            board=data["board"],
            title=data["title"],
            defaults={
                "description": data["description"],
                "status": data["status"],
                "priority": data["priority"],
                "due_date": data["due_date"],
                "assignee": data["assignee"],
                "reviewer": data["reviewer"],
            }
        )
        if created:
            print(f"Task created: {task.title}")
        else:
            print(f"Task exists: {task.title}")

        # Kommentare anlegen
        for comment_text in data["comments"]:
            comment, created = Comment.objects.get_or_create(
                task=task,
                author=user,
                content=comment_text
            )
            if created:
                print(f'Comment added to "{task.title}": {comment_text}')
            else:
                print(f'Comment exists in "{task.title}": {comment_text}')

def main():
    guest_user = create_guest_user()
    boards = create_boards(guest_user)
    create_tasks(boards, guest_user)
    print("Seed-Daten erfolgreich erstellt!")

if __name__ == "__main__":
    main()