from datetime import date, timedelta
from typing import TypedDict

from django.core.management.base import BaseCommand  # type: ignore

from apps.accounts.models import User  # type: ignore
from apps.exercise.models import Exercise  # type: ignore
from apps.workout.services import create_session  # type: ignore


class DayTemplate(TypedDict):
    day_in_week: int
    exercises: list[tuple[str, float, list[tuple[float, int]]]]


# Base weights for week 1 — each week adds a small increment
PUSH_DAY: DayTemplate = {
    'day_in_week': 0,  # Monday
    'exercises': [
        ('Bench Press', 70.0, [(0, 8), (5, 6), (5, 5)]),  # (offset_kg, reps)
        ('Overhead Press', 35.0, [(0, 10), (2.5, 8), (2.5, 7)]),
        ('Incline Dumbbell Press', 24.0, [(0, 10), (0, 10), (0, 8)]),
        ('Tricep Pushdown', 20.0, [(0, 12), (0, 12), (0, 10)]),
        ('Lateral Raise', 8.0, [(0, 15), (0, 12)]),
    ],
}

PULL_DAY: DayTemplate = {
    'day_in_week': 2,  # Wednesday
    'exercises': [
        ('Deadlift', 100.0, [(0, 5), (10, 3), (10, 2)]),
        ('Barbell Row', 60.0, [(0, 8), (5, 6), (5, 5)]),
        ('Pull-up', 0.0, [(0, 8), (0, 7), (0, 6)]),
        ('Face Pull', 15.0, [(0, 15), (0, 12), (0, 12)]),
        ('Dumbbell Curl', 12.0, [(0, 12), (2, 10), (2, 8)]),
    ],
}

LEG_DAY: DayTemplate = {
    'day_in_week': 4,  # Friday
    'exercises': [
        ('Squat', 80.0, [(0, 8), (10, 5), (10, 4)]),
        ('Leg Press', 120.0, [(0, 12), (20, 10), (20, 8)]),
        ('Romanian Deadlift', 60.0, [(0, 10), (5, 8), (5, 8)]),
        ('Leg Curl', 30.0, [(0, 12), (0, 12), (0, 10)]),
        ('Calf Raise', 40.0, [(0, 15), (0, 15), (0, 12)]),
    ],
}

WEEKLY_TEMPLATES: list[DayTemplate] = [PUSH_DAY, PULL_DAY, LEG_DAY]

DEMO_USERNAME = 'william'
DEMO_PASSWORD = 'irontrack123'  # noqa: S105


class Command(BaseCommand):
    help = 'Seed demo user and 8 weeks of workout sessions'

    def handle(self, *args, **options):
        # Create or get demo user
        user, user_created = User.objects.get_or_create(
            username=DEMO_USERNAME,
            defaults={
                'first_name': 'William',
                'email': 'william@irontrack.dev',
            },
        )
        if user_created:
            user.set_password(DEMO_PASSWORD)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created demo user: {DEMO_USERNAME}'))
        else:
            self.stdout.write(f'Demo user already exists: {DEMO_USERNAME}')

        # Generate 8 weeks of sessions
        today = date.today()
        weeks = 8
        start_monday = today - timedelta(days=today.weekday()) - timedelta(weeks=weeks)
        sessions_created = 0

        for week_num in range(weeks):
            week_monday = start_monday + timedelta(weeks=week_num)
            progression = week_num * 2.5

            for template in WEEKLY_TEMPLATES:
                day_offset = int(template['day_in_week'])
                session_date = week_monday + timedelta(days=day_offset)

                if session_date > today:
                    continue

                exercises_payload = []
                for exercise_item in template['exercises']:
                    exercise_name, base_weight, sets_template = exercise_item
                    try:
                        exercise = Exercise.objects.get(name=exercise_name)
                    except Exercise.DoesNotExist:
                        self.stderr.write(self.style.WARNING(f'Exercise "{exercise_name}" not found — skipping'))
                        continue

                    sets = []
                    for offset_kg, reps in sets_template:
                        weight = float(base_weight) + float(offset_kg) + progression
                        sets.append({'weight': round(weight, 1), 'reps': int(reps)})  # type: ignore

                    exercises_payload.append(
                        {
                            'exercise_id': exercise.id,
                            'sets': sets,
                        }
                    )

                if exercises_payload:
                    create_session(
                        {'date': str(session_date), 'exercises': exercises_payload},
                        user=user,
                    )
                    sessions_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {sessions_created} workout sessions'))
