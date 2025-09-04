
Zastępstwa – PROSTA wersja, tylko dla admina (bez logowania).

Jak uruchomić:
1) python -m venv .venv && .venv\Scripts\activate (Windows) lub source .venv/bin/activate (Linux/Mac)
2) pip install django
3) cd serwer
4) python manage.py migrate
5) python manage.py seed_simple
6) python manage.py runserver
7) Wejdź na http://127.0.0.1:8000/

Widoki:
- "/" (kalendarz) – wybór wykładowcy na górze; kliknięcie zajęć -> formularz dodania zastępstwa
- "/substitutions/new?session_id=ID"

REST (proste JSON):
- GET  /api/lecturers
- GET  /api/events?lecturer_id=<id optional>
- POST /api/substitutions   body: {"session_id":<int>, "lecturer_id":<int>}
- POST /api/mark_needs      body: {"session_id":<int>, "needs":true|false}

Algorytmy w zastepstwa/services.py:
- kwalifikacje przedmiotu vs kwalifikacje wykładowcy
- kolizja czasowa zajęć
- limit zastępstw / tydzień
- limit łącznych godzin nauczania / tydzień

Uwaga: Frontend korzysta z FullCalendar z CDN.
