from datetime import date, timedelta

from django.db.models import F, FloatField, Sum
from django.db.models.functions import TruncWeek

from apps.workout.models import SetLog, WorkoutSession  # type: ignore


def get_all_sessions(user):
    return (
        WorkoutSession.objects.filter(user=user)
        .annotate(
            total_volume=Sum(
                F('exercise_logs__sets__weight') * F('exercise_logs__sets__reps'), output_field=FloatField()
            )
        )
        .order_by('-date')
    )


def get_session_by_id(session_id, user):
    return WorkoutSession.objects.get(id=session_id, user=user)


def get_dashboard_stats(timespan, user):
    days_map = {'1W': 7, '1M': 30, '3M': 90}
    days = days_map.get(timespan, 30)
    since = date.today() - timedelta(days=days)

    sets_in_range = SetLog.objects.filter(
        exercise_log__session__user=user,
        exercise_log__session__date__gte=since,
    )
    sessions_in_range = WorkoutSession.objects.filter(user=user, date__gte=since)

    # 1. Volume by muscle category
    volume_by_category = list(
        sets_in_range.values(category=F('exercise_log__exercise__category'))
        .annotate(volume=Sum(F('weight') * F('reps'), output_field=FloatField()))
        .order_by('-volume')
    )

    # 2. Total volume
    totals = sets_in_range.aggregate(total_volume=Sum(F('weight') * F('reps'), output_field=FloatField()))

    # 3. Session count
    session_count = sessions_in_range.count()

    # 4. Average volume by plan type
    sessions_with_volume = (
        sessions_in_range.filter(plan__isnull=False)
        .annotate(
            session_volume=Sum(
                F('exercise_logs__sets__weight') * F('exercise_logs__sets__reps'),
                output_field=FloatField(),
            )
        )
        .values('plan__type', 'session_volume')
    )
    plan_type_totals: dict[str, list[float]] = {}
    for row in sessions_with_volume:
        pt = row['plan__type']
        vol = row['session_volume'] or 0
        plan_type_totals.setdefault(pt, []).append(vol)
    avg_by_plan_type = [
        {'plan_type': pt, 'avg_volume': sum(vols) / len(vols)} for pt, vols in sorted(plan_type_totals.items())
    ]

    # 5. Weekly volume buckets
    weekly_volume = list(
        sets_in_range.annotate(week=TruncWeek('exercise_log__session__date'))
        .values('week')
        .annotate(volume=Sum(F('weight') * F('reps'), output_field=FloatField()))
        .order_by('week')
    )

    return {
        'volume_by_category': volume_by_category,
        'total_volume': totals['total_volume'] or 0,
        'session_count': session_count,
        'avg_volume_by_plan_type': avg_by_plan_type,
        'weekly_volume': [{'week_start': str(w['week']), 'volume': w['volume']} for w in weekly_volume],
    }
