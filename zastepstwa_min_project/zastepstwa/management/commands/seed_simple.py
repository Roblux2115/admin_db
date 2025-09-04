
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time
from zastepstwa.models import Qualification, Subject, Lecturer, ClassSession

class Command(BaseCommand):
    help = "Tworzy przykładowe dane: wykładowcy, kwalifikacje, przedmioty, kilka zajęć na tydzień."

    def handle(self, *args, **options):
        # Quals
        q_math, _ = Qualification.objects.get_or_create(code="Q1", defaults={"name": "Matematyka"})
        q_cs,   _ = Qualification.objects.get_or_create(code="Q2", defaults={"name": "Informatyka"})
        q_phy,  _ = Qualification.objects.get_or_create(code="Q3", defaults={"name": "Fizyka"})

        # Subjects
        s_math, _ = Subject.objects.get_or_create(code="MATH", defaults={"name": "Analiza matematyczna"})
        s_cs,   _ = Subject.objects.get_or_create(code="CS",   defaults={"name": "Algorytmy"})
        s_phy,  _ = Subject.objects.get_or_create(code="PHY",  defaults={"name": "Fizyka I"})
        s_math.required_qualifications.set([q_math])
        s_cs.required_qualifications.set([q_cs])
        s_phy.required_qualifications.set([q_phy])

        # Lecturers
        a, _ = Lecturer.objects.get_or_create(first_name="Alicja", last_name="Kowalska", email="alicja@example.com")
        b, _ = Lecturer.objects.get_or_create(first_name="Bartek", last_name="Nowak", email="bartek@example.com")
        c, _ = Lecturer.objects.get_or_create(first_name="Celina", last_name="Wiśniewska", email="celina@example.com")
        d, _ = Lecturer.objects.get_or_create(first_name="Dawid",  last_name="Zieliński", email="dawid@example.com")
        a.qualifications.set([q_math])
        b.qualifications.set([q_cs])
        c.qualifications.set([q_phy])
        d.qualifications.set([q_math, q_cs])

        # Unavailabities
        

        now = timezone.localtime()
        base = now.date() + timedelta(days=(7 - now.weekday()))  # start od najbliższego poniedziałku

        slots = [
            (time(9,0),  time(10,30)),
            (time(11,0), time(12,30)),
            (time(13,0), time(14,30)),
            (time(15,0), time(16,30)),
        ]
        def mkdt(day, t): return timezone.make_aware(timezone.datetime.combine(day, t))

        plan = [
            (a, s_math, 0, 0),
            (a, s_math, 2, 1),
            (b, s_cs,   1, 2),
            (b, s_cs,   3, 3),
            (c, s_phy,  0, 1),
            (c, s_phy,  4, 2),
            (d, s_math, 2, 0),
            (d, s_cs,   4, 3),
        ]
        created = 0
        for who, subj, day_off, slot_i in plan:
            day = base + timedelta(days=day_off)
            start = mkdt(day, slots[slot_i][0])
            end   = mkdt(day, slots[slot_i][1])
            ClassSession.objects.get_or_create(subject=subj, lecturer=who, start=start, end=end)

        self.stdout.write(self.style.SUCCESS("✓ Dane demo dodane. Otwórz / aby zobaczyć kalendarz."))
