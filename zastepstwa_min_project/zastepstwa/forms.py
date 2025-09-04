from django import forms
from django.utils import timezone
from .models import ClassSession, Subject, Lecturer, Qualification
from collections import defaultdict

# zastepstwa/forms.py
from collections import defaultdict
from django import forms
from django.utils import timezone
from .models import ClassSession, Subject, Lecturer, Qualification


class ClassSessionForm(forms.ModelForm):
    class Meta:
        model = ClassSession
        fields = ["subject", "lecturer", "start", "end", "needs_substitution"]
        widgets = {
            "start": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start")
        end = cleaned.get("end")

        # Ujednolicenie do aware, jeśli USE_TZ=True
        if start and timezone.is_naive(start):
            cleaned["start"] = timezone.make_aware(start)
        if end and timezone.is_naive(end):
            cleaned["end"] = timezone.make_aware(end)

        if cleaned.get("start") and cleaned.get("end") and cleaned["end"] <= cleaned["start"]:
            raise forms.ValidationError("Koniec zajęć musi być po początku.")

        # prosta kolizja własnych zajęć prowadzącego
        lecturer = cleaned.get("lecturer")
        if lecturer and cleaned.get("start") and cleaned.get("end"):
            conflict = ClassSession.objects.filter(
                lecturer=lecturer,
                start__lt=cleaned["end"],
                end__gt=cleaned["start"]
            ).exists()
            if conflict:
                raise forms.ValidationError("Ten prowadzący ma już inne zajęcia w tym czasie.")
        return cleaned


class SubjectForm(forms.ModelForm):
    required_qualifications = forms.ModelMultipleChoiceField(
        queryset=Qualification.objects.all().order_by("code"),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Subject
        fields = ["code", "name", "required_qualifications"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ⬇️ Checkboxy pokazują TYLKO Q-kody
        self.fields["required_qualifications"].label_from_instance = lambda q: q.code


class LecturerForm(forms.ModelForm):
    qualifications = forms.ModelMultipleChoiceField(
        queryset=Qualification.objects.all().order_by("code"),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Lecturer
        fields = [
            "first_name", "last_name", "email",
            "qualifications",
            "max_substitutions_per_week", "max_hours_per_week",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # kwalifikacja_id -> [lista przedmiotów wymagających tej kwalifikacji]
        qual_to_subjects = defaultdict(list)
        for subj in Subject.objects.only("code", "name").prefetch_related("required_qualifications"):
            for q in subj.required_qualifications.all():
                # Co pokazać przy Q: kod – nazwa przedmiotu (zmień na samo code jeśli wolisz)
                qual_to_subjects[q.id].append(f"{subj.code} – {subj.name}")

        def label_from_q(q: Qualification):
            items = sorted(qual_to_subjects.get(q.id, []))
            if not items:
                # ⬇️ TYLKO Q-kod + informacja o braku przedmiotów
                return f"{q.code}\n(brak powiązanych przedmiotów)"
            MAX = 6  # ile wypisać wprost
            preview = "\n• " + "\n• ".join(items[:MAX])
            more = f" (+{len(items)-MAX} więcej)" if len(items) > MAX else ""
            # ⬇️ TYLKO Q-kod + lista przedmiotów (bez nazw kwalifikacji)
            return f"{q.code}{preview}{more}"

        self.fields["qualifications"].label_from_instance = label_from_q