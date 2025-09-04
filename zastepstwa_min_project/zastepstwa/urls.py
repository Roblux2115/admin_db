# zastepstwa/urls.py
from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "zastepstwa"

urlpatterns = [
    # Kalendarz jako strona główna
    path("", views.calendar_view, name="calendar"),
    path("calendar/", RedirectView.as_view(pattern_name="zastepstwa:calendar", permanent=False)),

    # Dodawanie zwykłych zajęć
    path("sessions/new/", views.session_create, name="session_create"),

    # API do kalendarza i zastępstw
    path("api/events", views.api_events, name="api_events"),
    path("api/substitutions/preview", views.api_substitution_preview, name="api_substitution_preview"),
    path("api/substitutions", views.api_substitutions, name="api_substitutions"),

    # Formularz zastępstwa
    path("substitutions/new", views.substitution_form, name="substitution_new"),

    # Przedmioty CRUD
    path("subjects/", views.subjects_list, name="subjects_list"),
    path("subjects/new/", views.subject_new, name="subject_new"),
    path("subjects/<int:subject_id>/edit/", views.subject_edit, name="subject_edit"),
    path("subjects/<int:subject_id>/delete/", views.subject_delete, name="subject_delete"),

    # Wykładowcy CRUD
    path("lecturers/", views.lecturers_list, name="lecturers_list"),
    path("lecturers/new/", views.lecturer_new, name="lecturer_new"),
    path("lecturers/<int:lecturer_id>/edit/", views.lecturer_edit, name="lecturer_edit"),
    path("lecturers/<int:lecturer_id>/delete/", views.lecturer_delete, name="lecturer_delete"),

    path("stats/", views.stats_view, name="stats"),
]
