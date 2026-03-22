from datetime import date, timedelta

from django.core.management.base import BaseCommand

from apps.exercise.models import Exercise
from apps.workout.services import create_session


DEMO_SESSIONS = [
    {
        'date_offset': 0,
        'notes': 'Push day — felt strong',
        'exercises': [
            ('Bench Press', [(80.0, 8), (85.0, 6), (85.0, 5)]),
            ('Overhead Press', [(40.0, 10), (42.5, 8), (42.5, 7)]),
            ('Incline Dumbbell Press', [(30.0, 10), (30.0, 10), (30.0, 8)]),
            ('Tricep Pushdown', [(25.0, 12), (25.0, 12), (25.0, 10)]),
            ('Lateral Raise', [(10.0, 15), (10.0, 12)]),
        ],
    },
    {
        'date_offset': -2,
        'notes': 'Pull day',
        'exercises': [
            ('Deadlift', [(120.0, 5), (130.0, 3), (140.0, 1)]),
            ('Barbell Row', [(60.0, 10), (65.0, 8), (65.0, 7)]),
            ('Pull-up', [(0.0, 10), (0.0, 8), (0.0, 6)]),
            ('Face Pull', [(15.0, 15), (15.0, 15)]),
            ('Dumbbell Curl', [(12.0, 12), (14.0, 10), (14.0, 8)]),
        ],
    },
    {
        'date_offset': -4,
        'notes': 'Leg day',
        'exercises': [
            ('Squat', [(100.0, 8), (110.0, 5), (110.0, 5)]),
            ('Leg Press', [(180.0, 10), (200.0, 8), (200.0, 8)]),
            ('Romanian Deadlift', [(80.0, 10), (80.0, 10), (80.0, 8)]),
            ('Leg Curl', [(40.0, 12), (40.0, 12)]),
            ('Calf Raise', [(60.0, 15), (60.0, 15), (60.0, 12)]),
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed demo workout sessions (requires exercises to be seeded first)'

    def handle(self, *args, **options):
        today = date.today()
        created_count = 0

        for session_data in DEMO_SESSIONS:
            session_date = today + timedelta(days=session_data['date_offset'])

            exercises_payload = []
            for exercise_name, sets in session_data['exercises']:
                try:
                    exercise = Exercise.objects.get(name=exercise_name)
                except Exercise.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f'Exercise "{exercise_name}" not found — run seed_exercises first'))
                    return

                exercises_payload.append({
                    'exercise_id': exercise.id,
                    'sets': [{'weight': w, 'reps': r} for w, r in sets],
                })

            create_session({
                'date': str(session_date),
                'notes': session_data['notes'],
                'exercises': exercises_payload,
            })
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} demo sessions'))
