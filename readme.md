# KanMind Backend

KanMind Backend is the server-side application for a task management app where users can register, create boards, and add tasks. Tasks can have comments, and both boards and tasks support roles such as creators and members.

## Technologies

- Python
- Django
- Django REST Framework

## Features

- User registration and authentication
- Board creation and management
- Task creation within boards
- Commenting on tasks
- Role management for creators and members on boards and tasks

## Installation

1. Clone the repository:
   git clone <repository-url>
   cd <repository-folder>

2. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate   # On Windows use venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Run the development server:
   python manage.py runserver

5. (Optional) Populate test data:
   python manage.py shell < populate_test_data.py

## Database

The project uses SQLite (db.sqlite3), which is automatically created when running the server for the first time.

## API Documentation

Detailed API endpoint documentation is available here:  
https://cdn.developerakademie.com/courses/Backend/EndpointDoku/index.html?name=kanmind

## License

MIT License

Copyright (c) 2025 Henrik Petersen

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, subject to the following conditions:

1. The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
2. The backend portion of this project was developed by Henrik Petersen.
3. The frontend portion is provided by Developer Akademie and used here with permission. All rights for the frontend remain with its original creators.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.






