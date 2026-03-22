from django.db import transaction

from apps.exercise.models import Exercise
from apps.plan.models import Plan, PlanExercise, PlanWeekly, PlanWeeklyItem


def create_plan(data):
    name = data.get('name')
    if not name:
        raise ValueError('name is required')

    plan_type = data.get('type')
    if not plan_type:
        raise ValueError('type is required')

    exercises = data.get('exercises', [])

    # Validate exercise IDs
    if exercises:
        exercise_ids = [e['exercise_id'] for e in exercises]
        existing_ids = set(Exercise.objects.filter(id__in=exercise_ids).values_list('id', flat=True))
        for ex in exercises:
            if ex['exercise_id'] not in existing_ids:
                raise ValueError(f'Exercise with id {ex["exercise_id"]} does not exist')

    with transaction.atomic():
        plan = Plan.objects.create(name=name, type=plan_type)

        for order_index, ex_data in enumerate(exercises):
            PlanExercise.objects.create(
                plan=plan,
                exercise_id=ex_data['exercise_id'],
                target_sets=ex_data.get('target_sets'),
                target_reps=ex_data.get('target_reps'),
                order_index=order_index,
            )

    return plan


def create_plan_weekly(data):
    name = data.get('name')
    if not name:
        raise ValueError('name is required')

    items = data.get('items', [])

    # Validate plan IDs
    if items:
        plan_ids = [item['plan_id'] for item in items]
        existing_ids = set(Plan.objects.filter(id__in=plan_ids).values_list('id', flat=True))
        for item in items:
            if item['plan_id'] not in existing_ids:
                raise ValueError(f'Plan with id {item["plan_id"]} does not exist')

        # Validate day_of_week values
        for item in items:
            if item['day_of_week'] < 1 or item['day_of_week'] > 7:
                raise ValueError(f'day_of_week must be between 1 and 7, got {item["day_of_week"]}')

    with transaction.atomic():
        plan_weekly = PlanWeekly.objects.create(name=name)

        for item_data in items:
            PlanWeeklyItem.objects.create(
                plan_weekly=plan_weekly,
                plan_id=item_data['plan_id'],
                day_of_week=item_data['day_of_week'],
            )

    return plan_weekly
