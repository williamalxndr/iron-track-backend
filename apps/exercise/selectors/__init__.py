from django.db.models import F, FloatField, Max

from apps.exercise.models import Exercise  # type: ignore
from apps.workout.models import ExerciseLog, SetLog  # type: ignore


def get_all_exercises():
    return Exercise.objects.all().order_by('name')


def get_exercise_history(exercise_id, user):
    exercise = Exercise.objects.get(id=exercise_id)
    logs = (
        ExerciseLog.objects.filter(exercise=exercise, session__user=user)
        .select_related('session')
        .prefetch_related('sets')
        .order_by('-session__date')
    )
    result = []
    for log in logs:
        sets = [{'weight': s.weight, 'reps': s.reps} for s in log.sets.all().order_by('set_number')]
        result.append({'date': str(log.session.date), 'sets': sets})
    return result


def get_exercise_stats(exercise_id, user):
    exercise = Exercise.objects.get(id=exercise_id)
    qs = SetLog.objects.filter(
        exercise_log__exercise=exercise,
        exercise_log__session__user=user,
    )
    stats = qs.aggregate(
        max_weight=Max('weight'),
        max_reps=Max('reps'),
        max_volume=Max(F('weight') * F('reps'), output_field=FloatField()),
    )
    return {
        'max_weight': stats['max_weight'] or 0,
        'max_reps': stats['max_reps'] or 0,
        'max_volume': stats['max_volume'] or 0,
    }
