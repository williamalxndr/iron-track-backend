from apps.workout.models import WorkoutSession


def get_all_sessions():
    return WorkoutSession.objects.all().order_by('-date')


def get_session_by_id(session_id):
    return WorkoutSession.objects.get(id=session_id)
