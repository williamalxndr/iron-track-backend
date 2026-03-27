from django.core.management.base import BaseCommand  # type: ignore

from apps.exercise.models import Exercise  # type: ignore
from apps.plan.models import Plan, PlanExercise, PlanWeekly, PlanWeeklyItem  # type: ignore

TEMPLATE_PLANS = [
    {
        'name': 'Cbum Push Day',
        'type': 'PUSH',
        'exercises': ['Bench Press', 'Overhead Press', 'Incline Dumbbell Press', 'Tricep Pushdown', 'Lateral Raise'],
    },
    {
        'name': 'Cbum Pull Day',
        'type': 'PULL',
        'exercises': ['Deadlift', 'Barbell Row', 'Pull-up', 'Face Pull', 'Dumbbell Curl'],
    },
    {
        'name': 'Sam Sulek Leg Day',
        'type': 'LEG',
        'exercises': ['Squat', 'Leg Press', 'Romanian Deadlift', 'Leg Curl', 'Calf Raise'],
    },
]

TEMPLATE_WEEKLY = {
    'name': 'Classic PPL',
    'items': [
        # day_of_week: 1=Monday ... 7=Sunday
        {'plan_name': 'Cbum Push Day', 'day_of_week': 1},
        {'plan_name': 'Cbum Pull Day', 'day_of_week': 3},
        {'plan_name': 'Sam Sulek Leg Day', 'day_of_week': 5},
    ],
}


class Command(BaseCommand):
    help = 'Seed template plans and weekly schedules'

    def handle(self, *args, **options):
        created_plans = 0
        for tpl in TEMPLATE_PLANS:
            plan, was_created = Plan.objects.get_or_create(
                name=tpl['name'],
                is_template=True,
                defaults={'type': tpl['type'], 'user': None},
            )
            if was_created:
                created_plans += 1
                for i, ex_name in enumerate(tpl['exercises']):
                    try:
                        exercise = Exercise.objects.get(name=ex_name)
                    except Exercise.DoesNotExist:
                        self.stderr.write(self.style.WARNING(f'Exercise "{ex_name}" not found — skipping'))
                        continue
                    PlanExercise.objects.create(plan=plan, exercise=exercise, order_index=i)

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_plans} template plans'))

        # Weekly schedule
        weekly, weekly_created = PlanWeekly.objects.get_or_create(
            name=TEMPLATE_WEEKLY['name'],
            is_template=True,
            defaults={'user': None},
        )
        if weekly_created:
            for item in TEMPLATE_WEEKLY['items']:
                try:
                    plan = Plan.objects.get(name=item['plan_name'], is_template=True)
                except Plan.DoesNotExist:
                    continue
                PlanWeeklyItem.objects.create(
                    plan_weekly=weekly,
                    plan=plan,
                    day_of_week=item['day_of_week'],
                )
            self.stdout.write(self.style.SUCCESS('Seeded template weekly schedule'))
        else:
            self.stdout.write('Template weekly schedule already exists')
