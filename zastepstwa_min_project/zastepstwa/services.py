
from datetime import datetime, date, time, timedelta
from typing import Tuple
from django.utils import timezone
from django.db.models import Q, Sum, F, ExpressionWrapper, DurationField
from .models import ClassSession, Lecturer, Subject, Substitution
from django.core.exceptions import FieldError

def week_bounds(dt):
    # tydzień pon-ndz [start, end)
    monday = dt - timedelta(days=dt.weekday())
    start = timezone.make_aware(timezone.datetime(monday.year, monday.month, monday.day, 0,0,0))
    end = start + timedelta(days=7)
    return start, end

def overlaps(a_start, a_end, b_start, b_end) -> bool:
    return max(a_start, b_start) < min(a_end, b_end)

def has_qualifications(lecturer: Lecturer, subject: Subject) -> bool:
    required = set(subject.required_qualifications.values_list("id", flat=True))
    if not required:
        return True
    have = set(lecturer.qualifications.values_list("id", flat=True))
    return required.issubset(have)

def has_time_conflict(lecturer: Lecturer, start, end) -> bool:
    # czy ma inne zajecia (swoje lub w zastępstwie) w tym czasie
    own = ClassSession.objects.filter(lecturer=lecturer, start__lt=end, end__gt=start)
    as_sub = ClassSession.objects.filter(substitutions__substitute=lecturer, start__lt=end, end__gt=start)
    return own.exists() or as_sub.exists()

def weekly_counts(lecturer: Lecturer, when):
    ws, we = week_bounds(when)
    subs = Substitution.objects.filter(substitute=lecturer, session__start__gte=ws, session__start__lt=we).count()
    duration = ExpressionWrapper(F('end') - F('start'), output_field=DurationField())
    own_hours = ClassSession.objects.filter(lecturer=lecturer, start__gte=ws, start__lt=we).aggregate(total=Sum(duration))['total'] or timezone.timedelta()
    sub_hours = ClassSession.objects.filter(substitutions__substitute=lecturer, start__gte=ws, start__lt=we).aggregate(total=Sum(duration))['total'] or timezone.timedelta()
    return subs, (own_hours + sub_hours)

def can_take_substitution(lecturer: Lecturer, session: ClassSession) -> Tuple[bool, str]:
    if not has_qualifications(lecturer, session.subject):
        return False, "Brak kwalifikacji do tego przedmiotu."
    if has_time_conflict(lecturer, session.start, session.end):
        return False, "Kolizja w grafiku – inne zajęcia w tym czasie."
    subs_count, total_hours = weekly_counts(lecturer, session.start)
    duration = (session.end - session.start)
    if subs_count + 1 > lecturer.max_substitutions_per_week:
        return False, f"Przekroczysz limit zastępstw na tydzień ({lecturer.max_substitutions_per_week})."
    hours_num = (total_hours + duration).total_seconds() / 3600
    if hours_num > lecturer.max_hours_per_week:
        return False, f"Przekroczysz limit godzin na tydzień ({lecturer.max_hours_per_week}h)."
    return True, "OK"

def _week_bounds(dt):
    """Zwraca poniedziałek 00:00 i początek następnego poniedziałku w lokalnej strefie."""
    tz = timezone.get_current_timezone()
    dt_local = timezone.localtime(dt, tz)
    monday = dt_local.date() - timedelta(days=dt_local.weekday())
    start = timezone.make_aware(datetime.combine(monday, time(0, 0)), tz)
    end = start + timedelta(days=7)
    return start, end

def _overlap_q(start, end):
    # A.start < B.end AND A.end > B.start
    return Q(start__lt=end, end__gt=start)

def evaluate_substitution(lecturer, session):
    """
    Zwraca szczegóły walidacji kandydata dla danego zastępstwa:
    - kwalifikacje
    - dostępność czasową
    - limity: liczba zastępstw/tydzień i godziny/tydzień (po dodaniu tego zastępstwa)
    """
    # 1) kwalifikacje
    req_ids = set(session.subject.required_qualifications.values_list("id", flat=True))
    have_ids = set(lecturer.qualifications.values_list("id", flat=True))
    has_required = req_ids.issubset(have_ids)

    # 2) wolny termin (własne zajęcia + te, gdzie już zastępuje)
    try:
        conflict_qs = ClassSession.objects.filter(
            Q(lecturer=lecturer) | Q(substitutions__substitute=lecturer)
        )
    except FieldError:
        # fallback na ewentualne related_name='substitution'
        conflict_qs = ClassSession.objects.filter(
            Q(lecturer=lecturer) | Q(substitution__substitute=lecturer)
        )

    conflict = conflict_qs.filter(_overlap_q(session.start, session.end))\
                          .exclude(id=session.id)\
                          .exists()
    is_free = not conflict

    # 3) granice tygodnia wg terminu TEGO zastępstwa
    week_start, week_end = _week_bounds(session.start)

    # 4) liczba zastępstw w tygodniu (po dodaniu tego)
    subs_week = Substitution.objects.filter(
        substitute=lecturer,
        session__start__gte=week_start,
        session__start__lt=week_end,
    ).count()
    subs_week_after = subs_week + 1
    subs_limit = int(lecturer.max_substitutions_per_week or 0)
    subs_ok = (subs_limit == 0) or (subs_week_after <= subs_limit)

    # 5) godziny/tydzień (własne + przyjęte zastępstwa)
    try:
        week_sessions = ClassSession.objects.filter(
            Q(lecturer=lecturer) | Q(substitutions__substitute=lecturer),
            start__gte=week_start, start__lt=week_end
        ).distinct()
    except FieldError:
        week_sessions = ClassSession.objects.filter(
            Q(lecturer=lecturer) | Q(substitution__substitute=lecturer),
            start__gte=week_start, start__lt=week_end
        ).distinct()

    def hours_sum(qs):
        total = 0.0
        for s in qs:
            total += (s.end - s.start).total_seconds() / 3600.0
        return total

    hours_week_now = hours_sum(week_sessions)
    this_hours = (session.end - session.start).total_seconds() / 3600.0
    hours_week_after = hours_week_now + this_hours
    hours_limit = float(lecturer.max_hours_per_week or 0)
    hours_ok = (hours_limit == 0.0) or (hours_week_after <= hours_limit)

    qualifications = list(lecturer.qualifications.values_list("code", flat=True))
    required_codes = list(session.subject.required_qualifications.values_list("code", flat=True))

    ok = has_required and is_free and subs_ok and hours_ok

    return {
        "ok": ok,
        "qualifications": qualifications,
        "required": required_codes,
        "has_required": has_required,
        "is_free": is_free,

        "subs_week_now": subs_week,
        "subs_week_after": subs_week_after,
        "subs_limit": subs_limit,
        "subs_ok": subs_ok,

        "hours_week_now": round(hours_week_now, 2),
        "hours_week_after": round(hours_week_after, 2),
        "hours_limit": hours_limit,
        "hours_ok": hours_ok,
        "this_hours": round(this_hours, 2),
    }
