from django.db import IntegrityError
from django.test import TestCase

from apps.exercise.models import Exercise


class ExerciseModelTest(TestCase):
    def test_create_exercise(self):
        exercise = Exercise.objects.create(name='Bench Press', category='Push')
        self.assertEqual(exercise.name, 'Bench Press')
        self.assertEqual(exercise.category, 'Push')
        self.assertIsNotNone(exercise.created_at)

    def test_name_is_required(self):
        with self.assertRaises(IntegrityError):
            Exercise.objects.create(name=None)

    def test_category_is_optional(self):
        exercise = Exercise.objects.create(name='Deadlift')
        self.assertIsNone(exercise.category)

    def test_str(self):
        exercise = Exercise.objects.create(name='Squat')
        self.assertEqual(str(exercise), 'Squat')

    def test_db_table_name(self):
        self.assertEqual(Exercise._meta.db_table, 'exercise')
