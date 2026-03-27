from django.db import transaction

from apps.exercise.models import Exercise  # type: ignore
from apps.plan.models import Plan, PlanExercise, PlanWeekly, PlanWeeklyItem  # type: ignore


def create_plan(data, user):
    name = data.get('name', '').strip()
    plan_type = data.get('type', '').strip()

    if not name:
        raise ValueError('Plan name is required')
    if not plan_type:
        raise ValueError('Plan type is required')

    with transaction.atomic():
        plan = Plan.objects.create(
            user=user,
            name=name,
            type=plan_type,
            is_template=False,
        )

        for i, ex_data in enumerate(data.get('exercises', [])):
            exercise_id = ex_data.get('exercise_id')
            try:
                exercise = Exercise.objects.get(id=exercise_id)
            except Exercise.DoesNotExist:
                raise ValueError(f'Exercise with id {exercise_id} does not exist') from None

            PlanExercise.objects.create(
                plan=plan,
                exercise=exercise,
                order_index=i,
            )

    return plan


def update_plan(plan_id, data, user):
    plan = Plan.objects.get(id=plan_id, user=user, is_template=False)

    name = data.get('name', '').strip()
    plan_type = data.get('type', '').strip()

    if not name:
        raise ValueError('Plan name is required')
    if not plan_type:
        raise ValueError('Plan type is required')

    with transaction.atomic():
        plan.name = name
        plan.type = plan_type
        plan.save()

        plan.exercises.all().delete()

        for i, ex_data in enumerate(data.get('exercises', [])):
            exercise_id = ex_data.get('exercise_id')
            try:
                exercise = Exercise.objects.get(id=exercise_id)
            except Exercise.DoesNotExist:
                raise ValueError(f'Exercise with id {exercise_id} does not exist') from None

            PlanExercise.objects.create(
                plan=plan,
                exercise=exercise,
                order_index=i,
            )

    return plan


def delete_plan(plan_id, user):
    plan = Plan.objects.get(id=plan_id, user=user, is_template=False)
    plan.delete()


def create_plan_weekly(data, user):
    name = data.get('name', '').strip()
    if not name:
        raise ValueError('Weekly plan name is required')

    with transaction.atomic():
        weekly = PlanWeekly.objects.create(
            user=user,
            name=name,
            is_template=False,
        )

        for item_data in data.get('items', []):
            plan_id = item_data.get('plan_id')
            day_of_week = item_data.get('day_of_week')

            if not (1 <= day_of_week <= 7):
                raise ValueError(f'Invalid day_of_week: {day_of_week}')

            try:
                plan = Plan.objects.get(id=plan_id)
            except Plan.DoesNotExist:
                raise ValueError(f'Plan with id {plan_id} does not exist') from None

            PlanWeeklyItem.objects.create(
                plan_weekly=weekly,
                plan=plan,
                day_of_week=day_of_week,
            )

    return weekly
