from datetime import date

from django.core.management import call_command
from django.db import IntegrityError
from django.db.models import QuerySet
from django.test import TestCase

from apps.exercise.models import Exercise
from apps.exercise.selectors import get_all_exercises, get_exercise_history, get_exercise_stats
from apps.exercise.serializers import ExerciseSerializer
from apps.workout.models import ExerciseLog, SetLog, WorkoutSession


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

    # image_url tests
    def test_create_exercise_with_image_url(self):
        url = 'https://example.supabase.co/storage/v1/object/public/exercises/bench-press.png'
        exercise = Exercise.objects.create(name='Bench Press', category='Push', image_url=url)
        self.assertEqual(exercise.image_url, url)

    def test_image_url_is_optional(self):
        exercise = Exercise.objects.create(name='Deadlift')
        self.assertIsNone(exercise.image_url)

    def test_image_url_max_length(self):
        long_url = 'https://example.com/' + 'a' * 475
        exercise = Exercise.objects.create(name='Squat', image_url=long_url)
        self.assertEqual(exercise.image_url, long_url)


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

    def test_serializes_image_url_field(self):
        url = 'https://example.supabase.co/storage/v1/object/public/exercises/squat.png'
        exercise = Exercise.objects.create(name='Squat', category='Legs', image_url=url)
        data = ExerciseSerializer(exercise).data
        self.assertEqual(data['image_url'], url)

    def test_serializes_null_image_url(self):
        exercise = Exercise.objects.create(name='Deadlift')
        data = ExerciseSerializer(exercise).data
        self.assertIsNone(data['image_url'])

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
        self.assertIn('image_url', exercise)
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


# ── History Selector Tests ──────────────────────────────────────────


class ExerciseHistorySelectorTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')
        self.other_exercise = Exercise.objects.create(name='Squat', category='Legs')

        session1 = WorkoutSession.objects.create(date=date(2026, 3, 22))
        log1 = ExerciseLog.objects.create(session=session1, exercise=self.exercise)
        SetLog.objects.create(exercise_log=log1, set_number=1, weight=80.0, reps=8)
        SetLog.objects.create(exercise_log=log1, set_number=2, weight=80.0, reps=6)

        session2 = WorkoutSession.objects.create(date=date(2026, 3, 20))
        log2 = ExerciseLog.objects.create(session=session2, exercise=self.exercise)
        SetLog.objects.create(exercise_log=log2, set_number=1, weight=77.5, reps=8)

        # Other exercise log (should not appear in bench press history)
        log3 = ExerciseLog.objects.create(session=session1, exercise=self.other_exercise)
        SetLog.objects.create(exercise_log=log3, set_number=1, weight=100.0, reps=5)

    # Positive
    def test_get_exercise_history_returns_sets_grouped_by_date(self):
        history = get_exercise_history(self.exercise.id)
        self.assertEqual(len(history), 2)
        self.assertEqual(len(history[0]['sets']), 2)
        self.assertEqual(len(history[1]['sets']), 1)

    def test_get_exercise_history_ordered_by_date_desc(self):
        history = get_exercise_history(self.exercise.id)
        self.assertEqual(history[0]['date'], date(2026, 3, 22))
        self.assertEqual(history[1]['date'], date(2026, 3, 20))

    def test_get_exercise_history_only_for_given_exercise(self):
        history = get_exercise_history(self.exercise.id)
        all_weights = [s['weight'] for entry in history for s in entry['sets']]
        self.assertNotIn(100.0, all_weights)

    # Corner
    def test_get_exercise_history_empty(self):
        empty_exercise = Exercise.objects.create(name='Deadlift')
        history = get_exercise_history(empty_exercise.id)
        self.assertEqual(history, [])

    # Negative
    def test_get_exercise_history_exercise_not_found(self):
        with self.assertRaises(Exercise.DoesNotExist):
            get_exercise_history(9999)


# ── Stats Selector Tests ────────────────────────────────────────────


class ExerciseStatsSelectorTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')
        session = WorkoutSession.objects.create(date=date(2026, 3, 22))
        log = ExerciseLog.objects.create(session=session, exercise=self.exercise)
        SetLog.objects.create(exercise_log=log, set_number=1, weight=100.0, reps=5)  # volume=500
        SetLog.objects.create(exercise_log=log, set_number=2, weight=80.0, reps=10)  # volume=800
        SetLog.objects.create(exercise_log=log, set_number=3, weight=60.0, reps=12)  # volume=720

    # Positive
    def test_get_exercise_stats_max_weight(self):
        stats = get_exercise_stats(self.exercise.id)
        self.assertEqual(stats['max_weight'], 100.0)

    def test_get_exercise_stats_max_reps(self):
        stats = get_exercise_stats(self.exercise.id)
        self.assertEqual(stats['max_reps'], 12)

    def test_get_exercise_stats_max_volume(self):
        stats = get_exercise_stats(self.exercise.id)
        self.assertEqual(stats['max_volume'], 800.0)

    # Corner
    def test_get_exercise_stats_no_sets(self):
        empty_exercise = Exercise.objects.create(name='Deadlift')
        stats = get_exercise_stats(empty_exercise.id)
        self.assertEqual(stats, {'max_weight': 0, 'max_reps': 0, 'max_volume': 0})

    def test_get_exercise_stats_single_set(self):
        ex = Exercise.objects.create(name='OHP')
        session = WorkoutSession.objects.create(date=date(2026, 3, 21))
        log = ExerciseLog.objects.create(session=session, exercise=ex)
        SetLog.objects.create(exercise_log=log, set_number=1, weight=40.0, reps=8)
        stats = get_exercise_stats(ex.id)
        self.assertEqual(stats['max_weight'], 40.0)
        self.assertEqual(stats['max_reps'], 8)
        self.assertEqual(stats['max_volume'], 320.0)

    # Negative
    def test_get_exercise_stats_exercise_not_found(self):
        with self.assertRaises(Exercise.DoesNotExist):
            get_exercise_stats(9999)


# ── History View Tests ──────────────────────────────────────────────


class ExerciseHistoryViewTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')
        session = WorkoutSession.objects.create(date=date(2026, 3, 22))
        log = ExerciseLog.objects.create(session=session, exercise=self.exercise)
        SetLog.objects.create(exercise_log=log, set_number=1, weight=80.0, reps=8)

    # Positive
    def test_history_200(self):
        response = self.client.get(f'/api/v1/exercises/{self.exercise.id}/history/')
        self.assertEqual(response.status_code, 200)

    def test_history_response_format(self):
        response = self.client.get(f'/api/v1/exercises/{self.exercise.id}/history/')
        data = response.json()
        self.assertIn('data', data)
        self.assertIn('message', data)
        self.assertIsInstance(data['data'], list)
        self.assertIn('date', data['data'][0])
        self.assertIn('sets', data['data'][0])

    def test_history_sets_contain_weight_and_reps(self):
        response = self.client.get(f'/api/v1/exercises/{self.exercise.id}/history/')
        s = response.json()['data'][0]['sets'][0]
        self.assertIn('weight', s)
        self.assertIn('reps', s)

    # Corner
    def test_history_empty_returns_empty_array(self):
        empty_ex = Exercise.objects.create(name='Deadlift')
        response = self.client.get(f'/api/v1/exercises/{empty_ex.id}/history/')
        data = response.json()
        self.assertEqual(data['data'], [])
        self.assertEqual(data['message'], 'success')

    # Negative
    def test_history_exercise_not_found_404(self):
        response = self.client.get('/api/v1/exercises/9999/history/')
        self.assertEqual(response.status_code, 404)

    def test_history_post_not_allowed_405(self):
        response = self.client.post(f'/api/v1/exercises/{self.exercise.id}/history/')
        self.assertEqual(response.status_code, 405)


# ── Stats View Tests ────────────────────────────────────────────────


class ExerciseStatsViewTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')
        session = WorkoutSession.objects.create(date=date(2026, 3, 22))
        log = ExerciseLog.objects.create(session=session, exercise=self.exercise)
        SetLog.objects.create(exercise_log=log, set_number=1, weight=100.0, reps=5)

    # Positive
    def test_stats_200(self):
        response = self.client.get(f'/api/v1/exercises/{self.exercise.id}/stats/')
        self.assertEqual(response.status_code, 200)

    def test_stats_response_contains_fields(self):
        response = self.client.get(f'/api/v1/exercises/{self.exercise.id}/stats/')
        data = response.json()['data']
        self.assertIn('max_weight', data)
        self.assertIn('max_reps', data)
        self.assertIn('max_volume', data)

    # Corner
    def test_stats_no_sets_returns_zeros(self):
        empty_ex = Exercise.objects.create(name='Deadlift')
        response = self.client.get(f'/api/v1/exercises/{empty_ex.id}/stats/')
        data = response.json()['data']
        self.assertEqual(data, {'max_weight': 0, 'max_reps': 0, 'max_volume': 0})

    # Negative
    def test_stats_exercise_not_found_404(self):
        response = self.client.get('/api/v1/exercises/9999/stats/')
        self.assertEqual(response.status_code, 404)

    def test_stats_post_not_allowed_405(self):
        response = self.client.post(f'/api/v1/exercises/{self.exercise.id}/stats/')
        self.assertEqual(response.status_code, 405)
