from datetime import date as date_type

from django.db import transaction  # type: ignore

from apps.exercise.models import Exercise  # type: ignore
from apps.plan.models import Plan  # type: ignore
from apps.workout.models import ExerciseLog, SetLog, WorkoutSession  # type: ignore


def create_session(data, user):
    date_value = data.get('date')
    if isinstance(date_value, str):
        date_value = date_type.fromisoformat(date_value)
    if not date_value:
        date_value = date_type.today()

    plan_id = data.get('plan_id')
    plan = None
    if plan_id:
        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            raise ValueError(f'Plan with id {plan_id} does not exist') from None

    exercises = data.get('exercises', [])

    with transaction.atomic():
        session = WorkoutSession.objects.create(
            user=user,
            date=date_value,
            plan=plan,
        )

        for i, ex_data in enumerate(exercises):
            exercise_id = ex_data.get('exercise_id')
            try:
                exercise = Exercise.objects.get(id=exercise_id)
            except Exercise.DoesNotExist:
                raise ValueError(f'Exercise with id {exercise_id} does not exist') from None

            sets = ex_data.get('sets', [])
            if not sets:
                raise ValueError(f'Exercise {exercise.name} must have at least one set')

            log = ExerciseLog.objects.create(
                session=session,
                exercise=exercise,
                order_index=i,
            )

            for j, set_data in enumerate(sets):
                SetLog.objects.create(
                    exercise_log=log,
                    set_number=j + 1,
                    weight=set_data['weight'],
                    reps=set_data['reps'],
                )

    return session


def update_session(session_id, data, user):
    session = WorkoutSession.objects.get(id=session_id, user=user)

    date_value = data.get('date')
    if isinstance(date_value, str):
        date_value = date_type.fromisoformat(date_value)

    # If date is not provided in update, keep original session date
    if not date_value:
        date_value = session.date

    plan_id = data.get('plan_id')
    plan = None
    if plan_id:
        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            raise ValueError(f'Plan with id {plan_id} does not exist') from None

    with transaction.atomic():
        session.date = date_value
        session.plan = plan
        session.save()

        # Replace exercise logs
        session.exercise_logs.all().delete()

        for i, ex_data in enumerate(data.get('exercises', [])):
            exercise_id = ex_data.get('exercise_id')
            try:
                exercise = Exercise.objects.get(id=exercise_id)
            except Exercise.DoesNotExist:
                raise ValueError(f'Exercise with id {exercise_id} does not exist') from None

            sets = ex_data.get('sets', [])
            if not sets:
                raise ValueError(f'Exercise {exercise.name} must have at least one set')

            log = ExerciseLog.objects.create(
                session=session,
                exercise=exercise,
                order_index=i,
            )

            for j, set_data in enumerate(sets):
                SetLog.objects.create(
                    exercise_log=log,
                    set_number=j + 1,
                    weight=set_data['weight'],
                    reps=set_data['reps'],
                )

    return session


def delete_session(session_id, user):
    session = WorkoutSession.objects.get(id=session_id, user=user)
    session.delete()
