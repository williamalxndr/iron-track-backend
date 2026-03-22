from django.core.management.base import BaseCommand

from apps.exercise.models import Exercise

DEFAULT_EXERCISES = [
    ('Bench Press', 'Push'),
    ('Overhead Press', 'Push'),
    ('Incline Dumbbell Press', 'Push'),
    ('Tricep Pushdown', 'Push'),
    ('Lateral Raise', 'Push'),
    ('Squat', 'Legs'),
    ('Leg Press', 'Legs'),
    ('Romanian Deadlift', 'Legs'),
    ('Leg Curl', 'Legs'),
    ('Calf Raise', 'Legs'),
    ('Deadlift', 'Pull'),
    ('Barbell Row', 'Pull'),
    ('Pull-up', 'Pull'),
    ('Face Pull', 'Pull'),
    ('Dumbbell Curl', 'Pull'),
]


class Command(BaseCommand):
    help = 'Seed default exercises'

    def handle(self, *args, **options):
        created_count = 0
        for name, category in DEFAULT_EXERCISES:
            _, created = Exercise.objects.get_or_create(name=name, defaults={'category': category})
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} exercises ({Exercise.objects.count()} total)'))
