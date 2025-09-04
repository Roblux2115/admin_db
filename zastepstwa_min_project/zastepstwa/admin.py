from django.contrib import admin
from .models import Subject, Lecturer, ClassSession, Substitution


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email",
                    "max_substitutions_per_week", "max_hours_per_week")
    search_fields = ("first_name", "last_name", "email")
    filter_horizontal = ("subjects",)  # przedmioty = „uprawnienia”


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ("subject", "lecturer", "start", "end", "needs_substitution")
    list_filter = ("needs_substitution", "lecturer", "subject")
    search_fields = ("subject__code", "subject__name",
                     "lecturer__first_name", "lecturer__last_name")
    autocomplete_fields = ("subject", "lecturer")


@admin.register(Substitution)
class SubstitutionAdmin(admin.ModelAdmin):
    list_display = ("session", "substitute_lecturer", "created_at")
    search_fields = ("session__subject__code", "session__subject__name",
                     "substitute_lecturer__first_name", "substitute_lecturer__last_name")
    autocomplete_fields = ("session", "substitute_lecturer")
