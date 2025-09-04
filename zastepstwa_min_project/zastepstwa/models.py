from django.db import models

class Qualification(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.code} – {self.name}"


class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    # jakie kwalifikacje są wymagane do nauczania tego przedmiotu
    required_qualifications = models.ManyToManyField(
        Qualification, blank=True, related_name="subjects_required_for"
    )

    def __str__(self):
        return f"{self.code}: {self.name}"


class Lecturer(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(blank=True)

    # kwalifikacje jakie posiada prowadzący (Q1, Q2…)
    qualifications = models.ManyToManyField(
        Qualification, blank=True, related_name="lecturers"
    )
    # przedmioty które może prowadzić (opcjonalne; poglądowo)
    subjects = models.ManyToManyField(Subject, blank=True, related_name="lecturers")

    # limity
    max_substitutions_per_week = models.IntegerField(default=3)
    max_hours_per_week = models.FloatField(default=20.0)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ClassSession(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    needs_substitution = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} | {self.lecturer} | {self.start:%Y-%m-%d %H:%M}"


class Substitution(models.Model):
    # jeden wpis zastępstwa na jedne zajęcia
    session = models.OneToOneField(ClassSession, on_delete=models.CASCADE, related_name='substitution')
    # ← KLUCZ: pole może być puste, bo dopuszczamy “Brak”
    substitute_lecturer = models.ForeignKey(
        Lecturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taken_substitutions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.substitute_lecturer or "BRAK"
        return f"Zastępstwo({self.session_id}) → {target}"