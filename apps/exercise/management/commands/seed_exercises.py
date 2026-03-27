from django.core.management.base import BaseCommand  # type: ignore

from apps.exercise.models import Exercise  # type: ignore

EXERCISES = [
    ('Bench Press', 'Chest'),
    ('Incline Dumbbell Press', 'Chest'),
    ('Cable Fly', 'Chest'),
    ('Overhead Press', 'Shoulders'),
    ('Lateral Raise', 'Shoulders'),
    ('Cable Front Raise', 'Shoulders'),
    ('Cable Lateral Raise', 'Shoulders'),
    ('Face Pull', 'Shoulders'),
    ('Squat', 'Quads'),
    ('Leg Press', 'Quads'),
    ('Leg Extension', 'Quads'),
    ('Romanian Deadlift', 'Hamstrings'),
    ('Leg Curl', 'Hamstrings'),
    ('Calf Raise', 'Calves'),
    ('Deadlift', 'Back'),
    ('Barbell Row', 'Back'),
    ('Cable Row', 'Back'),
    ('Chest Supported Row', 'Back'),
    ('Pull-up', 'Lats'),
    ('Lat Pulldown', 'Lats'),
    ('Shrug', 'Traps'),
    ('Tricep Pushdown', 'Triceps'),
    ('Skull Crusher', 'Triceps'),
    ('Dumbbell Curl', 'Biceps'),
    ('Barbell Curl', 'Biceps'),
    ('Hammer Curl', 'Brachialis'),
]


class Command(BaseCommand):
    help = 'Seed the exercise catalog'

    def handle(self, *args, **options):
        created = 0
        for name, category in EXERCISES:
            _, was_created = Exercise.objects.get_or_create(
                name=name,
                defaults={'category': category},
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Seeded {created} new exercises ({len(EXERCISES)} total)'))
