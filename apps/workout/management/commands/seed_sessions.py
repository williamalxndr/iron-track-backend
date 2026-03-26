from datetime import date, timedelta
from typing import TypedDict

from django.core.management.base import BaseCommand  # type: ignore

from apps.exercise.models import Exercise  # type: ignore
from apps.workout.services import create_session  # type: ignore


class ExerciseTemplate(TypedDict):
    name: str
    base_weight: float
    sets: list[tuple[float, int]]

class DayTemplate(TypedDict):
    day_in_week: int
    exercises: list[tuple[str, float, list[tuple[float, int]]]]

# Base weights for week 1 — each week adds a small increment
PUSH_DAY: DayTemplate = {
    'day_in_week': 0,  # Monday
    'exercises': [
        ('Bench Press', 70.0, [(0, 8), (5, 6), (5, 5)]),       # (offset_kg, reps)
        ('Overhead Press', 35.0, [(0, 10), (2.5, 8), (2.5, 7)]),
        ('Incline Dumbbell Press', 24.0, [(0, 10), (0, 10), (0, 8)]),
        ('Tricep Pushdown', 20.0, [(0, 12), (0, 12), (0, 10)]),
        ('Lateral Raise', 8.0, [(0, 15), (0, 12)]),
    ],
}

PULL_DAY: DayTemplate = {
    'day_in_week': 2,  # Wednesday
    'exercises': [
        ('Deadlift', 100.0, [(0, 5), (10, 3), (20, 1)]),
        ('Barbell Row', 50.0, [(0, 10), (5, 8), (5, 7)]),
        ('Pull-up', 0.0, [(0, 10), (0, 8), (0, 6)]),
        ('Face Pull', 12.5, [(0, 15), (0, 15)]),
        ('Dumbbell Curl', 10.0, [(0, 12), (2, 10), (2, 8)]),
    ],
}

LEG_DAY: DayTemplate = {
    'day_in_week': 4,  # Friday
    'exercises': [
        ('Squat', 80.0, [(0, 8), (10, 5), (10, 5)]),
        ('Leg Press', 140.0, [(0, 10), (20, 8), (20, 8)]),
        ('Romanian Deadlift', 60.0, [(0, 10), (0, 10), (0, 8)]),
        ('Leg Curl', 30.0, [(0, 12), (0, 12)]),
        ('Calf Raise', 40.0, [(0, 15), (0, 15), (0, 12)]),
    ],
}

WEEKLY_TEMPLATES: list[DayTemplate] = [PUSH_DAY, PULL_DAY, LEG_DAY]
NUM_WEEKS = 8

# Weekly weight progression per exercise (kg added per week)
WEEKLY_INCREMENT = 2.5


class Command(BaseCommand):
    help = 'Seed 8 weeks of demo workout sessions (requires exercises to be seeded first)'

    def handle(self, *args, **options):
        today = date.today()
        start_monday = today - timedelta(days=today.weekday()) - timedelta(days=(NUM_WEEKS - 1) * 7)
        created_count = 0

        if not Exercise.objects.exists():
            self.stderr.write(self.style.ERROR('No exercises found in database. Please run seed_exercises first.'))
            return

        for week in range(NUM_WEEKS):
            # timedelta(weeks=...) is valid, but let's be explicit with days for clarity if needed
            week_monday = start_monday + timedelta(days=week * 7)
            progression = float(week * WEEKLY_INCREMENT)

            for template in WEEKLY_TEMPLATES:
                day_offset = int(template['day_in_week'])
                session_date: date = week_monday + timedelta(days=day_offset)

                if session_date > today:
                    continue

                exercises_payload = []
                exercises_in_template = template['exercises']
                for exercise_item in exercises_in_template:
                    exercise_name, base_weight, sets_template = exercise_item
                    try:
                        exercise = Exercise.objects.get(name=exercise_name)
                    except Exercise.DoesNotExist:
                        self.stderr.write(
                            self.style.WARNING(
                                f'Exercise "{exercise_name}" not found — skipping this exercise'
                            )
                        )
                        continue

                    sets = []
                    for offset_kg, reps in sets_template:
                        weight = float(base_weight) + float(offset_kg) + progression
                        # round() with ndigits is standard, but IDE is confused
                        sets.append({'weight': round(weight, 1), 'reps': int(reps)})  # type: ignore

                    exercises_payload.append(
                        {
                            'exercise_id': exercise.id,
                            'sets': sets,
                        }
                    )

                create_session(
                    {
                        'date': str(session_date),
                        'exercises': exercises_payload,
                    }
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} demo sessions across {NUM_WEEKS} weeks'))
