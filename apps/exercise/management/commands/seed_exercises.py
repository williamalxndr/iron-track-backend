from django.core.management.base import BaseCommand

from apps.exercise.models import Exercise

DEFAULT_EXERCISES = [
    ('Bench Press', 'Chest'),
    ('Overhead Press', 'Shoulders'),
    ('Incline Dumbbell Press', 'Chest'),
    ('Tricep Pushdown', 'Triceps'),
    ('Lateral Raise', 'Shoulders'),
    ('Squat', 'Quads'),
    ('Leg Press', 'Quads'),
    ('Romanian Deadlift', 'Legs'),
    ('Leg Curl', 'Hamstrings'),
    ('Calf Raise', 'Calves'),
    ('Deadlift', 'Back'),
    ('Barbell Row', 'Back'),
    ('Pull-up', 'Lats'),
    ('Face Pull', 'Back'),
    ('Dumbbell Curl', 'Back'),
    ('Hammer Curl', 'Brachialis'),
    ('Preacher Curl', 'Biceps'),
    ('Lat Pulldown', 'Lats'),
    ('Cable Row', 'Back'),
    ('Chest Supported Row', 'Back'),
    ('Smith Machine Squat', 'Quads'),
    ('Smith Machine Bench Press', 'Chest'),
    ('Smith Machine Overhead Press', 'Shoulders'),
    ('Dumbbell Shrug', 'Traps'),
    ('Cable Lateral Raise', 'Shoulders'),
    ('Cable Front Raise', 'Shoulders'),
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
