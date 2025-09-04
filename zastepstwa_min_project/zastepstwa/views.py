from __future__ import annotations

from datetime import date, datetime, timedelta

from django import forms
from django.db.models import Q 
from django.db.models import (
    Sum, Count, F, DurationField, ExpressionWrapper,
    Min, Max,   # ← DODANE
)

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import Lecturer, Subject, ClassSession, Substitution
import json



# -------------------- Formularze --------------------

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["code", "name"]  # już bez required_qualifications


class LecturerForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = [
            "first_name", "last_name", "email",
            "subjects",  # tylko przedmioty określają uprawnienia
            "max_substitutions_per_week", "max_hours_per_week",
        ]
        widgets = {
            "subjects": forms.CheckboxSelectMultiple,
        }


class SessionForm(forms.ModelForm):
    class Meta:
        model = ClassSession
        fields = ["subject", "lecturer", "start", "end", "needs_substitution"]
        widgets = {
            "start": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


# -------------------- Pomocnicze --------------------

def _hours_between(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds() / 3600.0


def _week_bounds(dt: datetime):
    """Poniedziałek 00:00 -> poniedziałek +7 dni (w lokalnej strefie TZ)."""
    local = timezone.localtime(dt)
    week_start_date = local.date() - timedelta(days=local.weekday())
    week_start = datetime.combine(week_start_date, datetime.min.time(), tzinfo=local.tzinfo)
    week_end = week_start + timedelta(days=7)
    return week_start, week_end


def _overlaps(a_start, a_end, b_start, b_end) -> bool:
    return not (a_end <= b_start or b_end <= a_start)


# -------------------- Widoki główne --------------------

def calendar_view(request):
    lecturers = Lecturer.objects.order_by("last_name", "first_name")
    selected_id = request.GET.get("lecturer_id")
    try:
        selected_id = int(selected_id) if selected_id else None
    except ValueError:
        selected_id = None

    ctx = {"lecturers": lecturers, "selected_id": selected_id}
    return render(request, "zastepstwa/calendar.html", ctx)


def session_create(request):
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("zastepstwa:calendar")
    else:
        form = SessionForm()
    return render(request, "zastepstwa/session_form.html", {"form": form})


# -------------------- API dla kalendarza --------------------

def api_events(request):
    """
    Zwraca wydarzenia dla FullCalendar.
    GET: start, end (ISO8601 z TZ), opcjonalnie lecturer_id (filtr)
    """
    start_str = request.GET.get("start")
    end_str = request.GET.get("end")
    lecturer_id = request.GET.get("lecturer_id")

    start_dt = parse_datetime(start_str) if start_str else None
    end_dt = parse_datetime(end_str) if end_str else None

    qs = (
        ClassSession.objects
        .select_related("lecturer", "subject", "substitution__substitute_lecturer")
    )

    if start_dt and end_dt:
        qs = qs.filter(start__lt=end_dt, end__gt=start_dt)

    if lecturer_id:
        qs = qs.filter(
            Q(lecturer_id=lecturer_id) |
            Q(substitution__substitute_lecturer_id=lecturer_id)
        )

    events = []
    for sess in qs:
        sub = getattr(sess, "substitution", None)
        title_lines = [
            f"{sess.subject.name}",
            f"{sess.lecturer.first_name} {sess.lecturer.last_name}",
        ]
        color = None
        if sub and sub.substitute_lecturer_id:
            sl = sub.substitute_lecturer
            title_lines.append(f"Zastępstwo: {sl.first_name} {sl.last_name}")
            color = "#10b981"

        evt = {
            "id": sess.id,
            "title": "\n".join(title_lines),
            "start": sess.start.isoformat(),
            "end": sess.end.isoformat(),
        }
        if color:
            evt["color"] = color
        events.append(evt)

    return JsonResponse(events, safe=False)


# ----------------- STATYSTYKI -----------------
from django.db.models import (
    Sum, Count, F, DurationField, ExpressionWrapper,
    Min, Max,
)
from datetime import datetime, timedelta, date
import json

def _date_from_str(s: str | None) -> date | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None

def _period_bounds(request):
    """
    Zwraca (start_dt, end_dt, label). end ekskluzywne.
    Obsługuje period=week|month|custom|all
    """
    now = timezone.localtime()
    period = request.GET.get("period") or "month"

    if period == "week":
        start_date = now.date() - timedelta(days=now.weekday())
        end_date = start_date + timedelta(days=7)
        label = f"Tydzień {start_date} – {end_date - timedelta(days=1)}"

    elif period == "custom":
        def _d(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d").date()
            except Exception:
                return None
        s = _d(request.GET.get("start"))
        e = _d(request.GET.get("end"))
        if not s or not e or s > e:
            # fallback: ostatnie 30 dni
            e = now.date()
            s = e - timedelta(days=29)
        start_date, end_date = s, e + timedelta(days=1)
        label = f"Zakres {s} – {e}"

    elif period == "all":
        min_start = ClassSession.objects.order_by("start").values_list("start", flat=True).first()
        max_end   = ClassSession.objects.order_by("-end").values_list("end", flat=True).first()
        if not min_start or not max_end:
            start_date = now.date()
            end_date   = start_date + timedelta(days=1)
        else:
            start_date = timezone.localtime(min_start).date()
            end_date   = timezone.localtime(max_end).date() + timedelta(days=1)
        label = f"Cały okres"

    else:  # month
        start_date = now.replace(day=1).date()
        if start_date.month == 12:
            end_date = date(start_date.year + 1, 1, 1)
        else:
            end_date = date(start_date.year, start_date.month + 1, 1)
        label = f"Miesiąc {start_date:%Y-%m}"

    tz = now.tzinfo
    start_dt = datetime.combine(start_date, datetime.min.time(), tzinfo=tz)
    end_dt   = datetime.combine(end_date,   datetime.min.time(), tzinfo=tz)
    return start_dt, end_dt, label

def stats_view(request):
    """
    Ranking według zakresu:
      scope=subs  -> tylko przejęte zastępstwa (ale pokazujemy też wykładowców z 0)
      scope=all   -> realnie prowadzone godziny (własne nieprzejęte + przejęte)
    """
    start_dt, end_dt, period_label = _period_bounds(request)
    scope      = request.GET.get("scope") or "subs"   # subs | all
    metric     = request.GET.get("metric") or "hours" # hours | subs
    direction  = request.GET.get("dir") or "desc"

    # słownik z wszystkimi wykładowcami -> start z zerami
    lecturers = list(Lecturer.objects.order_by("last_name", "first_name")
                     .values("id", "first_name", "last_name"))
    data = {
        l["id"]: {"lecturer_id": l["id"],
                  "name": f'{l["first_name"]} {l["last_name"]}',
                  "subs": 0, "hours": 0.0}
        for l in lecturers
    }

    dur = ExpressionWrapper(F("end") - F("start"), output_field=DurationField())

    if scope == "subs":
        # Tylko zajęcia przejęte w zastępstwie
        rows = (
            ClassSession.objects
            .filter(start__gte=start_dt, start__lt=end_dt,
                    substitution__substitute_lecturer__isnull=False)
            .values("substitution__substitute_lecturer_id")
            .annotate(subs=Count("id"), dur=Sum(dur))
        )
        for r in rows:
            lid = r["substitution__substitute_lecturer_id"]
            if lid in data:
                data[lid]["subs"]  = int(r["subs"] or 0)
                data[lid]["hours"] = round(((r["dur"] or timedelta()).total_seconds() / 3600.0), 2)

    else:  # scope == "all"
        # Własne nieprzejęte
        own_rows = (
            ClassSession.objects
            .filter(start__gte=start_dt, start__lt=end_dt,
                    substitution__isnull=True)
            .values("lecturer_id")
            .annotate(dur=Sum(dur))
        )
        for r in own_rows:
            lid = r["lecturer_id"]
            if lid in data:
                data[lid]["hours"] += (r["dur"] or timedelta()).total_seconds() / 3600.0

        # Godziny i liczba zajęć przejętych jako zastępca
        taken_rows = (
            ClassSession.objects
            .filter(start__gte=start_dt, start__lt=end_dt,
                    substitution__substitute_lecturer__isnull=False)
            .values("substitution__substitute_lecturer_id")
            .annotate(subs=Count("id"), dur=Sum(dur))
        )
        for r in taken_rows:
            lid = r["substitution__substitute_lecturer_id"]
            if lid in data:
                data[lid]["subs"]  += int(r["subs"] or 0)
                data[lid]["hours"] += (r["dur"] or timedelta()).total_seconds() / 3600.0

        # zaokrąglij po zsumowaniu
        for v in data.values():
            v["hours"] = round(v["hours"], 2)

    # lista + sortowanie
    ranking = list(data.values())
    key = "hours" if metric == "hours" else "subs"
    ranking.sort(key=lambda r: r[key], reverse=(direction != "asc"))

    labels = [r["name"] for r in ranking]
    values_hours = [r["hours"] for r in ranking]
    values_subs  = [r["subs"]  for r in ranking]

    ctx = {
        "period_label": period_label,
        "start_val": request.GET.get("start", ""),
        "end_val": request.GET.get("end", ""),
        "selected_period": request.GET.get("period", "month"),
        "metric": metric,
        "direction": direction,
        "ranking": ranking,
        "labels_json": json.dumps(labels, ensure_ascii=False),
        "hours_json": json.dumps(values_hours),
        "subs_json": json.dumps(values_subs),
    }
    return render(request, "zastepstwa/stats.html", ctx)


# -------------------- Zastępstwa --------------------

def substitution_form(request):
    sid = request.GET.get("session_id")
    session = get_object_or_404(
        ClassSession.objects.select_related("subject", "lecturer"),
        id=sid
    )
    # kandydaci: wszyscy poza oryginalnym prowadzącym
    lecturers = Lecturer.objects.exclude(id=session.lecturer_id).order_by("last_name", "first_name")
    return render(
        request,
        "zastepstwa/substitution_new.html",
        {"session": session, "lecturers": lecturers},
    )


def api_substitution_preview(request):
    """
    GET ?session_id=&lecturer_id=
    Zwraca ocenę kandydata (czy prowadzi przedmiot, dostępność, limity).
    """
    try:
        sid = int(request.GET.get("session_id"))
        lid = int(request.GET.get("lecturer_id"))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("bad params")

    session = get_object_or_404(
        ClassSession.objects.select_related("subject", "lecturer"),
        id=sid
    )
    lecturer = get_object_or_404(Lecturer, id=lid)

    # 1) Czy prowadzi ten przedmiot (uprawnienia przez powiązanie subjects)?
    can_teach = lecturer.subjects.filter(id=session.subject_id).exists()

    # 2) Dostępność – liczymy realną zajętość
    def _slots_of(lect: Lecturer):
        # własne zajęcia BEZ zastępstwa (oddane nie liczą się jako jego obciążenie)
        qs_normal = ClassSession.objects.filter(
            lecturer=lect, substitution__isnull=True
        ).values_list("start", "end")
        # zajęcia przejęte jako zastępca
        qs_taken = ClassSession.objects.filter(
            substitution__substitute_lecturer=lect
        ).values_list("start", "end")
        return list(qs_normal) + list(qs_taken)

    is_free = True
    for a_start, a_end in _slots_of(lecturer):
        if _overlaps(a_start, a_end, session.start, session.end):
            is_free = False
            break

    # 3) Limity tygodniowe – liczymy tylko realne godziny
    week_start, week_end = _week_bounds(session.start)

    def _week_hours_and_subs(lect: Lecturer):
        normal = ClassSession.objects.filter(
            lecturer=lect, start__gte=week_start, start__lt=week_end,
            substitution__isnull=True
        )
        taken = ClassSession.objects.filter(
            substitution__substitute_lecturer=lect,
            start__gte=week_start, start__lt=week_end
        )

        hours = 0.0
        for s in list(normal) + list(taken):
            hours += _hours_between(s.start, s.end)

        subs_count = Substitution.objects.filter(
            substitute_lecturer=lect,
            session__start__gte=week_start, session__start__lt=week_end
        ).count()
        return hours, subs_count

    hours_before, subs_before = _week_hours_and_subs(lecturer)
    this_hours = _hours_between(session.start, session.end)
    hours_after = hours_before + this_hours
    subs_after = subs_before + 1

    subs_limit = lecturer.max_substitutions_per_week or 0
    hours_limit = lecturer.max_hours_per_week or 0.0

    subs_ok = (subs_limit == 0) or (subs_after <= subs_limit)
    hours_ok = (hours_limit == 0) or (hours_after <= hours_limit)
    overall_ok = can_teach and is_free and subs_ok and hours_ok

    return JsonResponse({
        "empty": False,
        "can_teach": can_teach,
        "is_free": is_free,
        "subs_week_after": subs_after,
        "subs_limit": subs_limit,
        "subs_ok": subs_ok,
        "hours_week_after": round(hours_after, 2),
        "hours_limit": hours_limit,
        "hours_ok": hours_ok,
        "ok": overall_ok,
    })


def api_substitution_preview(request):
    """
    GET ?session_id=&lecturer_id=
    Zwraca ocenę kandydata (czy prowadzi przedmiot, dostępność, limity)
    + listę przedmiotów, które prowadzi.
    """
    try:
        sid = int(request.GET.get("session_id"))
        lid = int(request.GET.get("lecturer_id"))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("bad params")

    session = get_object_or_404(
        ClassSession.objects.select_related("subject", "lecturer"),
        id=sid
    )
    lecturer = get_object_or_404(Lecturer, id=lid)

    # 1) uprawnienia do TEGO przedmiotu
    can_teach = lecturer.subjects.filter(id=session.subject_id).exists()

    # 2) dostępność – liczymy realne obciążenie
    def _slots_of(lect: Lecturer):
        # własne zajęcia bez zastępstwa
        qs_normal = ClassSession.objects.filter(
            lecturer=lect, substitution__isnull=True
        ).values_list("start", "end")
        # zajęcia wzięte jako zastępca
        qs_taken = ClassSession.objects.filter(
            substitution__substitute_lecturer=lect
        ).values_list("start", "end")
        return list(qs_normal) + list(qs_taken)

    is_free = True
    for a_start, a_end in _slots_of(lecturer):
        if _overlaps(a_start, a_end, session.start, session.end):
            is_free = False
            break

    # 3) limity tygodniowe – tylko realne godziny
    week_start, week_end = _week_bounds(session.start)

    def _week_hours_and_subs(lect: Lecturer):
        normal = ClassSession.objects.filter(
            lecturer=lect, start__gte=week_start, start__lt=week_end,
            substitution__isnull=True
        )
        taken = ClassSession.objects.filter(
            substitution__substitute_lecturer=lect,
            start__gte=week_start, start__lt=week_end
        )

        hours = 0.0
        for s in list(normal) + list(taken):
            hours += _hours_between(s.start, s.end)

        subs_count = Substitution.objects.filter(
            substitute_lecturer=lect,
            session__start__gte=week_start, session__start__lt=week_end
        ).count()
        return hours, subs_count

    hours_before, subs_before = _week_hours_and_subs(lecturer)
    this_hours = _hours_between(session.start, session.end)
    hours_after = hours_before + this_hours
    subs_after = subs_before + 1

    subs_limit = lecturer.max_substitutions_per_week or 0
    hours_limit = lecturer.max_hours_per_week or 0.0

    subs_ok = (subs_limit == 0) or (subs_after <= subs_limit)
    hours_ok = (hours_limit == 0) or (hours_after <= hours_limit)

    # lista przedmiotów prowadzonych przez kandydata (kod – nazwa)
    subjects_list = [
        f"{code} – {name}"
        for code, name in lecturer.subjects.values_list("code", "name")
    ]

    return JsonResponse({
        "empty": False,
        "subjects": subjects_list,    # ← NOWE
        "can_teach": can_teach,
        "is_free": is_free,
        "subs_week_after": subs_after,
        "subs_limit": subs_limit,
        "subs_ok": subs_ok,
        "hours_week_after": round(hours_after, 2),
        "hours_limit": hours_limit,
        "hours_ok": hours_ok,
        "ok": can_teach and is_free and subs_ok and hours_ok,
    })


# -------------------- Listy/CRUD --------------------

def subjects_list(request):
    subjects = Subject.objects.order_by("code", "name")
    return render(request, "zastepstwa/subjects_list.html", {"subjects": subjects})


def subject_new(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("zastepstwa:subjects_list")
    else:
        form = SubjectForm()
    return render(request, "zastepstwa/subject_form.html", {"form": form, "is_new": True})


def subject_edit(request, subject_id):
    subj = get_object_or_404(Subject, id=subject_id)
    if request.method == "POST":
        form = SubjectForm(request.POST, instance=subj)
        if form.is_valid():
            form.save()
            return redirect("zastepstwa:subjects_list")
    else:
        form = SubjectForm(instance=subj)
    return render(request, "zastepstwa/subject_form.html", {"form": form, "is_new": False})


def subject_delete(request, subject_id):
    subj = get_object_or_404(Subject, id=subject_id)
    subj.delete()
    return redirect("zastepstwa:subjects_list")


def lecturers_list(request):
    lecturers = Lecturer.objects.prefetch_related("subjects").order_by("last_name", "first_name")
    return render(request, "zastepstwa/lecturers_list.html", {"lecturers": lecturers})


def lecturer_new(request):
    if request.method == "POST":
        form = LecturerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("zastepstwa:lecturers_list")
    else:
        form = LecturerForm()
    return render(request, "zastepstwa/lecturer_form.html", {"form": form, "is_new": True})


def lecturer_edit(request, lecturer_id):
    lect = get_object_or_404(Lecturer, id=lecturer_id)
    if request.method == "POST":
        form = LecturerForm(request.POST, instance=lect)
        if form.is_valid():
            form.save()
            return redirect("zastepstwa:lecturers_list")
    else:
        form = LecturerForm(instance=lect)
    return render(request, "zastepstwa/lecturer_form.html", {"form": form, "is_new": False})


def lecturer_delete(request, lecturer_id):
    lect = get_object_or_404(Lecturer, id=lecturer_id)
    lect.delete()
    return redirect("zastepstwa:lecturers_list")


def _active_slots(lect: Lecturer):
    """
    Przedziały czasowe, które dany wykładowca REALNIE prowadzi
    (własne zajęcia nieprzejęte przez kogoś innego + zajęcia, które sam przejął).
    """
    own = ClassSession.objects.filter(
        lecturer=lect
    ).filter(
        Q(substitution__isnull=True) | Q(substitution__substitute_lecturer=lect)
    ).values_list("start", "end")

    taken = ClassSession.objects.filter(
        substitution__substitute_lecturer=lect
    ).values_list("start", "end")

    return list(own) + list(taken)


def api_substitutions(request):
    """
    POST JSON:
      { "session_id": <int>, "lecturer_id": <int> }  -> zapis
      { "session_id": <int>, "lecturer_id": "" }    -> wyczyszczenie
    Wymaga poprawnego CSRF (w szablonie wysyłamy X-CSRFToken).
    """
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    try:
        payload = json.loads(request.body.decode("utf-8"))
        sid = int(payload.get("session_id"))
        lid_raw = payload.get("lecturer_id")
        lid = None if lid_raw in ("", None) else int(lid_raw)
    except Exception:
        return HttpResponseBadRequest("bad json")

    session = get_object_or_404(ClassSession, id=sid)

    # wyczyszczenie zastępstwa
    if lid is None:
        Substitution.objects.filter(session=session).delete()
        return JsonResponse({"cleared": True})

    lecturer = get_object_or_404(Lecturer, id=lid)

    # 1) kandydat musi prowadzić dany przedmiot
    if not lecturer.subjects.filter(id=session.subject_id).exists():
        return JsonResponse({"ok": False, "reason": "Ten wykładowca nie prowadzi tego przedmiotu"})

    # 2) brak kolizji z realnie prowadzonymi zajęciami
    for a_start, a_end in _active_slots(lecturer):
        if _overlaps(a_start, a_end, session.start, session.end):
            return JsonResponse({"ok": False, "reason": "Kolizja w kalendarzu"})

    # 3) limity tygodniowe po dodaniu tej pozycji
    def _week_bounds(dt):
        local = timezone.localtime(dt)
        week_start_date = local.date() - timedelta(days=local.weekday())
        week_start = datetime.combine(week_start_date, datetime.min.time(), tzinfo=local.tzinfo)
        week_end = week_start + timedelta(days=7)
        return week_start, week_end

    def _hours_between(a, b):
        return (b - a).total_seconds() / 3600.0

    week_start, week_end = _week_bounds(session.start)

    hours = 0.0
    for s_start, s_end in _active_slots(lecturer):
        # liczymy tylko, jeśli wpada w ten tydzień (wystarczy sprawdzenie nakładania)
        if not (s_end <= week_start or s_start >= week_end):
            hours += _hours_between(s_start, s_end)
    hours += _hours_between(session.start, session.end)

    subs_count = (
        Substitution.objects.filter(
            substitute_lecturer=lecturer,
            session__start__gte=week_start,
            session__start__lt=week_end,
        ).count() + 1
    )

    if lecturer.max_substitutions_per_week and subs_count > lecturer.max_substitutions_per_week:
        return JsonResponse({"ok": False, "reason": "Przekroczony limit zastępstw w tygodniu"})

    if lecturer.max_hours_per_week and hours > lecturer.max_hours_per_week:
        return JsonResponse({"ok": False, "reason": "Przekroczony limit godzin w tygodniu"})

    # 4) zapis / aktualizacja
    Substitution.objects.update_or_create(
        session=session, defaults={"substitute_lecturer": lecturer}
    )
    return JsonResponse({"ok": True})

