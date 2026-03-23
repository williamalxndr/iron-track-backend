from django.db.models import F, FloatField, Sum

from apps.workout.models import WorkoutSession


def get_all_sessions():
    return (
        WorkoutSession.objects.all()
        .annotate(
            total_volume=Sum(
                F('exercise_logs__sets__weight') * F('exercise_logs__sets__reps'),
                output_field=FloatField(),
            )
        )
        .order_by('-date')
    )


def get_session_by_id(session_id):
    return WorkoutSession.objects.get(id=session_id)
