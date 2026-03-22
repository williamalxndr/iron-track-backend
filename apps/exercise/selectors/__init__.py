from apps.exercise.models import Exercise


def get_all_exercises():
    return Exercise.objects.all().order_by('name')
