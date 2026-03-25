from datetime import date as date_type

from django.db import transaction

from apps.exercise.models import Exercise
from apps.plan.models import Plan
from apps.workout.models import ExerciseLog, SetLog, WorkoutSession


def create_session(data):
    date_value = data.get('date')
    if not date_value:
        raise ValueError('date is required')

    exercises = data.get('exercises')
    if not exercises:
        raise ValueError('exercises is required')

    # Validate all exercise IDs exist and sets are non-empty
    exercise_ids = [e['exercise_id'] for e in exercises]
    existing_ids = set(Exercise.objects.filter(id__in=exercise_ids).values_list('id', flat=True))
    for ex in exercises:
        if ex['exercise_id'] not in existing_ids:
            raise ValueError(f'Exercise with id {ex["exercise_id"]} does not exist')
        if not ex.get('sets'):
            raise ValueError('Each exercise must have at least one set')

    # Parse date if string
    if isinstance(date_value, str):
        date_value = date_type.fromisoformat(date_value)

    plan_id = data.get('plan_id')
    plan = None
    if plan_id:
        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            raise ValueError(f'Plan with id {plan_id} does not exist')

    with transaction.atomic():
        session = WorkoutSession.objects.create(
            date=date_value,
            plan=plan,
        )

        for order_index, ex_data in enumerate(exercises):
            exercise_log = ExerciseLog.objects.create(
                session=session,
                exercise_id=ex_data['exercise_id'],
                order_index=order_index,
            )

            for set_number, set_data in enumerate(ex_data['sets'], start=1):
                SetLog.objects.create(
                    exercise_log=exercise_log,
                    set_number=set_number,
                    weight=set_data['weight'],
                    reps=set_data['reps'],
                )

    return session


def delete_session(session_id):
    session = WorkoutSession.objects.get(id=session_id)
    session.delete()


def update_session(session_id, data):
    session = WorkoutSession.objects.get(id=session_id)

    date_value = data.get('date')
    if not date_value:
        raise ValueError('date is required')

    exercises = data.get('exercises')
    if not exercises:
        raise ValueError('exercises is required')

    # Validate all exercise IDs exist and sets are non-empty
    exercise_ids = [e['exercise_id'] for e in exercises]
    existing_ids = set(Exercise.objects.filter(id__in=exercise_ids).values_list('id', flat=True))
    for ex in exercises:
        if ex['exercise_id'] not in existing_ids:
            raise ValueError(f'Exercise with id {ex["exercise_id"]} does not exist')
        if not ex.get('sets'):
            raise ValueError('Each exercise must have at least one set')

    # Parse date if string
    if isinstance(date_value, str):
        date_value = date_type.fromisoformat(date_value)

    plan_id = data.get('plan_id')
    plan = None
    if plan_id:
        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            raise ValueError(f'Plan with id {plan_id} does not exist')

    with transaction.atomic():
        session.date = date_value
        session.plan = plan
        session.save()

        # Delete old exercise logs (cascades to set logs)
        session.exercise_logs.all().delete()

        for order_index, ex_data in enumerate(exercises):
            exercise_log = ExerciseLog.objects.create(
                session=session,
                exercise_id=ex_data['exercise_id'],
                order_index=order_index,
            )

            for set_number, set_data in enumerate(ex_data['sets'], start=1):
                SetLog.objects.create(
                    exercise_log=exercise_log,
                    set_number=set_number,
                    weight=set_data['weight'],
                    reps=set_data['reps'],
                )

    return session
