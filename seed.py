import datetime
from django.contrib.auth import get_user_model
from .kanban_app.api.models import Board, Task, Comment
from django.db import transaction

User = get_user_model()

@transaction.atomic
def reset_and_seed():
    print("Alle Daten löschen...")

    Comment.objects.all().delete()
    Task.objects.all().delete()
    Board.objects.all().delete()
    User.objects.filter(email='guest@kanmind.de').delete()

    print("Guest-User anlegen...")
    guest_user = User.objects.create_user(
        username='guest',
        email='guest@kanmind.de',
        password='guestpassword',
    )

    print("Boards und Tasks anlegen...")
    board_titles = [
        "NextGen WebApp Development",
        "Mobile App Refactoring",
        "API Enhancement Sprint",
    ]
    boards = []
    for title in board_titles:
        board = Board.objects.create(title=title, owner=guest_user)
        board.members.add(guest_user)
        boards.append(board)

    tasks_data = [
        {
            "board": boards[0],
            "title": "API-Endpunkt für User-Authentifizierung erstellen",
            "description": "Implementiere einen REST-API-Endpunkt, der Benutzer-Login und Token-Generierung ermöglicht.",
            "status": "to-do",
            "priority": "high",
            "due_date": datetime.date.today() + datetime.timedelta(days=7),
            "assignee": guest_user,
            "reviewer": guest_user,
            "comments": [
                "Muss OAuth 2.0 unterstützen.",
                "Denk an Sicherheitslücken wie SQL-Injection.",
            ],
        },
        {
            "board": boards[0],
            "title": "UI-Design für Dashboard entwerfen",
            "description": "Erstelle erste Wireframes für das Admin-Dashboard mit Fokus auf Übersichtlichkeit.",
            "status": "to-do",
            "priority": "medium",
            "due_date": datetime.date.today() + datetime.timedelta(days=10),
            "assignee": guest_user,
            "reviewer": guest_user,
            "comments": [
                "Farbschema an die CI anpassen.",
                "Responsives Design nicht vergessen.",
            ],
        },
        {
            "board": boards[1],
            "title": "Datenbankmodell für Produktkatalog erweitern",
            "description": "Neue Tabellen und Beziehungen für Produktvarianten und Lagerbestand anlegen.",
            "status": "in-progress",
            "priority": "high",
            "due_date": datetime.date.today() + datetime.timedelta(days=5),
            "assignee": guest_user,
            "reviewer": guest_user,
            "comments": [
                "Überprüfe Indexierung für schnelle Abfragen.",
                "Migration muss rückwärtskompatibel sein.",
            ],
        },
        {
            "board": boards[1],
            "title": "Unit-Tests für Zahlungsmodul schreiben",
            "description": "Testfälle für Kreditkartenzahlungen und Fehlerbehandlung implementieren.",
            "status": "in-progress",
            "priority": "medium",
            "due_date": datetime.date.today() + datetime.timedelta(days=12),
            "assignee": guest_user,
            "reviewer": guest_user,
            "comments": [
                "Mocks für externe Zahlungs-API verwenden.",
                "Testabdeckung mindestens 80%.",
            ],
        },
        {
            "board": boards[2],
            "title": "Code-Review: Logging-Funktionalität optimieren",
            "description": "Überprüfung des Logging-Moduls auf Performance und Fehlerbehandlung.",
            "status": "review",
            "priority": "medium",
            "due_date": datetime.date.today() + datetime.timedelta(days=3),
            "assignee": guest_user,
            "reviewer": guest_user,
            "comments": [
                "Eventuelle Duplikate entfernen.",
                "Log-Level sollten konfigurierbar sein.",
            ],
        },
        {
            "board": boards[2],
            "title": "Dokumentation für Setup-Prozess aktualisieren",
            "description": "Readme um neue Installationsschritte und Umgebungsvariablen ergänzen.",
            "status": "review",
            "priority": "low",
            "due_date": datetime.date.today() + datetime.timedelta(days=8),
            "assignee": guest_user,
            "reviewer": guest_user,
            "comments": [
                "Screenshots für Windows und Mac ergänzen.",
                "Anleitung für Docker-Setup hinzufügen.",
            ],
        },
    ]

    for task_info in tasks_data:
        task = Task.objects.create(
            board=task_info["board"],
            title=task_info["title"],
            description=task_info["description"],
            status=task_info["status"],
            priority=task_info["priority"],
            due_date=task_info["due_date"],
            assignee=task_info["assignee"],
            reviewer=task_info["reviewer"],
        )
        for comment_text in task_info["comments"]:
            Comment.objects.create(task=task, author=guest_user, content=comment_text)

    print("Seed Daten wurden erfolgreich erstellt!")

if __name__ == "__main__":
    reset_and_seed()
