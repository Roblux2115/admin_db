to 

from .models import Lecturer, Subject, ClassSession, Substitution, LecturerUnavailability

na  W pliku zastepstwa/views.py
from .models import Lecturer, Subject, ClassSession, Substitution


wkonsoli wpisz 
python manage.py makemigrations
python manage.py migrate


from django.db import models

class LecturerUnavailability(models.Model):
    lecturer = models.ForeignKey('Lecturer', on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.lecturer} unavailable from {self.start} to {self.end}"
