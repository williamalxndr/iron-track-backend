from django.core.management import call_command
from django.db import IntegrityError
from django.db.models import QuerySet
from django.test import TestCase

from apps.exercise.models import Exercise
from apps.exercise.selectors import get_all_exercises
from apps.exercise.serializers import ExerciseSerializer


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


class ExerciseSelectorTest(TestCase):
    # Positive
    def test_get_all_exercises_returns_queryset(self):
        result = get_all_exercises()
        self.assertIsInstance(result, QuerySet)

    def test_get_all_exercises_returns_all(self):
        Exercise.objects.create(name='Bench Press', category='Push')
        Exercise.objects.create(name='Squat', category='Legs')
        Exercise.objects.create(name='Deadlift', category='Pull')
        result = get_all_exercises()
        self.assertEqual(result.count(), 3)

    # Corner
    def test_get_all_exercises_empty(self):
        result = get_all_exercises()
        self.assertEqual(result.count(), 0)

    def test_get_all_exercises_ordered_by_name(self):
        Exercise.objects.create(name='Squat')
        Exercise.objects.create(name='Bench Press')
        Exercise.objects.create(name='Deadlift')
        result = list(get_all_exercises().values_list('name', flat=True))
        self.assertEqual(result, ['Bench Press', 'Deadlift', 'Squat'])


class ExerciseSerializerTest(TestCase):
    # Positive
    def test_serializes_exercise_fields(self):
        exercise = Exercise.objects.create(name='Bench Press', category='Push')
        data = ExerciseSerializer(exercise).data
        self.assertEqual(data['id'], exercise.id)
        self.assertEqual(data['name'], 'Bench Press')
        self.assertEqual(data['category'], 'Push')
        self.assertIn('created_at', data)

    def test_serializes_null_category(self):
        exercise = Exercise.objects.create(name='Deadlift')
        data = ExerciseSerializer(exercise).data
        self.assertIsNone(data['category'])

    # Corner
    def test_serializes_multiple_exercises(self):
        Exercise.objects.create(name='Bench Press', category='Push')
        Exercise.objects.create(name='Squat', category='Legs')
        exercises = Exercise.objects.all()
        data = ExerciseSerializer(exercises, many=True).data
        self.assertEqual(len(data), 2)


class ExerciseListViewTest(TestCase):
    # Positive
    def test_list_exercises_200(self):
        response = self.client.get('/api/v1/exercises/')
        self.assertEqual(response.status_code, 200)

    def test_response_format(self):
        response = self.client.get('/api/v1/exercises/')
        data = response.json()
        self.assertIn('data', data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'success')

    def test_response_data_contains_exercises(self):
        Exercise.objects.create(name='Bench Press', category='Push')
        Exercise.objects.create(name='Squat', category='Legs')
        response = self.client.get('/api/v1/exercises/')
        data = response.json()
        self.assertEqual(len(data['data']), 2)

    def test_exercise_fields_in_response(self):
        Exercise.objects.create(name='Bench Press', category='Push')
        response = self.client.get('/api/v1/exercises/')
        exercise = response.json()['data'][0]
        self.assertIn('id', exercise)
        self.assertIn('name', exercise)
        self.assertIn('category', exercise)
        self.assertIn('created_at', exercise)

    # Corner
    def test_list_exercises_empty(self):
        response = self.client.get('/api/v1/exercises/')
        data = response.json()
        self.assertEqual(data['data'], [])
        self.assertEqual(data['message'], 'success')

    # Negative
    def test_post_not_allowed(self):
        response = self.client.post('/api/v1/exercises/')
        self.assertEqual(response.status_code, 405)


class SeedExercisesCommandTest(TestCase):
    # Positive
    def test_seed_creates_exercises(self):
        call_command('seed_exercises')
        self.assertGreater(Exercise.objects.count(), 0)

    # Corner - idempotent
    def test_seed_idempotent(self):
        call_command('seed_exercises')
        count_first = Exercise.objects.count()
        call_command('seed_exercises')
        count_second = Exercise.objects.count()
        self.assertEqual(count_first, count_second)
