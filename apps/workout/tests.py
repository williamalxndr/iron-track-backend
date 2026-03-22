from datetime import date

from django.db import IntegrityError
from django.test import TestCase

from apps.exercise.models import Exercise
from apps.workout.models import ExerciseLog, SetLog, WorkoutSession


class WorkoutSessionModelTest(TestCase):
    def test_create_session(self):
        session = WorkoutSession.objects.create(date=date(2026, 3, 22))
        self.assertEqual(session.date, date(2026, 3, 22))
        self.assertIsNotNone(session.created_at)

    def test_date_is_required(self):
        with self.assertRaises(IntegrityError):
            WorkoutSession.objects.create(date=None)

    def test_notes_is_optional(self):
        session = WorkoutSession.objects.create(date=date(2026, 3, 22))
        self.assertIsNone(session.notes)

    def test_str(self):
        session = WorkoutSession.objects.create(date=date(2026, 3, 22))
        self.assertEqual(str(session), 'Session 2026-03-22')

    def test_db_table_name(self):
        self.assertEqual(WorkoutSession._meta.db_table, 'workout_session')


class ExerciseLogModelTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')
        self.session = WorkoutSession.objects.create(date=date(2026, 3, 22))

    def test_create_exercise_log(self):
        log = ExerciseLog.objects.create(
            session=self.session,
            exercise=self.exercise,
        )
        self.assertEqual(log.session, self.session)
        self.assertEqual(log.exercise, self.exercise)
        self.assertEqual(log.order_index, 0)

    def test_order_index_default(self):
        log = ExerciseLog.objects.create(session=self.session, exercise=self.exercise)
        self.assertEqual(log.order_index, 0)

    def test_cascade_delete_session(self):
        ExerciseLog.objects.create(session=self.session, exercise=self.exercise)
        self.session.delete()
        self.assertEqual(ExerciseLog.objects.count(), 0)

    def test_cascade_delete_exercise(self):
        ExerciseLog.objects.create(session=self.session, exercise=self.exercise)
        self.exercise.delete()
        self.assertEqual(ExerciseLog.objects.count(), 0)

    def test_str(self):
        log = ExerciseLog.objects.create(session=self.session, exercise=self.exercise)
        self.assertEqual(str(log), f'{self.exercise.name} in {self.session}')

    def test_db_table_name(self):
        self.assertEqual(ExerciseLog._meta.db_table, 'exercise_log')


class SetLogModelTest(TestCase):
    def setUp(self):
        exercise = Exercise.objects.create(name='Squat')
        session = WorkoutSession.objects.create(date=date(2026, 3, 22))
        self.exercise_log = ExerciseLog.objects.create(session=session, exercise=exercise)

    def test_create_set_log(self):
        s = SetLog.objects.create(
            exercise_log=self.exercise_log,
            set_number=1,
            weight=100.0,
            reps=8,
        )
        self.assertEqual(s.weight, 100.0)
        self.assertEqual(s.reps, 8)
        self.assertEqual(s.set_number, 1)
        self.assertIsNotNone(s.created_at)

    def test_weight_is_required(self):
        with self.assertRaises(IntegrityError):
            SetLog.objects.create(
                exercise_log=self.exercise_log,
                set_number=1,
                weight=None,
                reps=8,
            )

    def test_reps_is_required(self):
        with self.assertRaises(IntegrityError):
            SetLog.objects.create(
                exercise_log=self.exercise_log,
                set_number=1,
                weight=60.0,
                reps=None,
            )

    def test_set_number_is_optional(self):
        s = SetLog.objects.create(
            exercise_log=self.exercise_log,
            weight=60.0,
            reps=10,
        )
        self.assertIsNone(s.set_number)

    def test_cascade_delete_exercise_log(self):
        SetLog.objects.create(exercise_log=self.exercise_log, weight=60.0, reps=8)
        self.exercise_log.delete()
        self.assertEqual(SetLog.objects.count(), 0)

    def test_str(self):
        s = SetLog.objects.create(exercise_log=self.exercise_log, set_number=1, weight=80.0, reps=5)
        self.assertEqual(str(s), 'Set 1: 80.0kg x 5')

    def test_db_table_name(self):
        self.assertEqual(SetLog._meta.db_table, 'set_log')
