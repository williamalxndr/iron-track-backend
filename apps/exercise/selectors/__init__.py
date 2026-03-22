from django.db.models import F, FloatField, Max

from apps.exercise.models import Exercise
from apps.workout.models import ExerciseLog, SetLog


def get_all_exercises():
    return Exercise.objects.all().order_by('name')


def get_exercise_history(exercise_id):
    exercise = Exercise.objects.get(id=exercise_id)

    logs = (
        ExerciseLog.objects.filter(exercise=exercise)
        .select_related('session')
        .prefetch_related('sets')
        .order_by('-session__date')
    )

    history = []
    for log in logs:
        sets = [{'weight': s.weight, 'reps': s.reps} for s in log.sets.order_by('set_number')]
        history.append({
            'date': log.session.date,
            'sets': sets,
        })
    return history


def get_exercise_stats(exercise_id):
    exercise = Exercise.objects.get(id=exercise_id)

    stats = (
        SetLog.objects.filter(exercise_log__exercise=exercise)
        .annotate(volume=F('weight') * F('reps'))
        .aggregate(
            max_weight=Max('weight'),
            max_reps=Max('reps'),
            max_volume=Max('volume', output_field=FloatField()),
        )
    )

    return {
        'max_weight': stats['max_weight'] or 0,
        'max_reps': stats['max_reps'] or 0,
        'max_volume': stats['max_volume'] or 0,
    }
