import json
from datetime import date

from django.db import IntegrityError
from django.db.models import QuerySet
from django.test import TestCase

from apps.exercise.models import Exercise
from apps.workout.models import ExerciseLog, SetLog, WorkoutSession
from apps.workout.selectors import get_all_sessions, get_session_by_id
from apps.workout.serializers import SessionDetailSerializer, SessionListSerializer
from apps.workout.services import create_session, delete_session, update_session


class WorkoutSessionModelTest(TestCase):
    def test_create_session(self):
        session = WorkoutSession.objects.create(date=date(2026, 3, 22))
        self.assertEqual(session.date, date(2026, 3, 22))
        self.assertIsNotNone(session.created_at)

    def test_date_is_required(self):
        with self.assertRaises(IntegrityError):
            WorkoutSession.objects.create(date=None)

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


# ── Selector Tests ──────────────────────────────────────────────────


class SessionSelectorTest(TestCase):
    # Positive
    def test_get_all_sessions_returns_queryset(self):
        result = get_all_sessions()
        self.assertIsInstance(result, QuerySet)

    def test_get_all_sessions_returns_all(self):
        WorkoutSession.objects.create(date=date(2026, 3, 20))
        WorkoutSession.objects.create(date=date(2026, 3, 22))
        result = get_all_sessions()
        self.assertEqual(result.count(), 2)

    def test_get_all_sessions_ordered_by_date_desc(self):
        WorkoutSession.objects.create(date=date(2026, 3, 18))
        WorkoutSession.objects.create(date=date(2026, 3, 22))
        WorkoutSession.objects.create(date=date(2026, 3, 20))
        dates = list(get_all_sessions().values_list('date', flat=True))
        self.assertEqual(dates, [date(2026, 3, 22), date(2026, 3, 20), date(2026, 3, 18)])

    # Corner
    def test_get_all_sessions_empty(self):
        result = get_all_sessions()
        self.assertEqual(result.count(), 0)

    # Positive
    def test_get_session_by_id_returns_session(self):
        session = WorkoutSession.objects.create(date=date(2026, 3, 22))
        result = get_session_by_id(session.id)
        self.assertEqual(result.id, session.id)

    # Negative
    def test_get_session_by_id_not_found_raises(self):
        with self.assertRaises(WorkoutSession.DoesNotExist):
            get_session_by_id(9999)


# ── Service Tests ───────────────────────────────────────────────────


class SessionServiceTest(TestCase):
    def setUp(self):
        self.exercise1 = Exercise.objects.create(name='Bench Press', category='Push')
        self.exercise2 = Exercise.objects.create(name='Overhead Press', category='Push')

    # Positive
    def test_create_session_basic(self):
        data = {
            'date': '2026-03-22',
            'exercises': [
                {
                    'exercise_id': self.exercise1.id,
                    'sets': [{'weight': 80.0, 'reps': 8}],
                },
            ],
        }
        session = create_session(data)
        self.assertEqual(session.date, date(2026, 3, 22))

    def test_create_session_with_exercises_and_sets(self):
        data = {
            'date': '2026-03-22',
            'exercises': [
                {
                    'exercise_id': self.exercise1.id,
                    'sets': [{'weight': 80.0, 'reps': 8}, {'weight': 80.0, 'reps': 6}],
                },
                {
                    'exercise_id': self.exercise2.id,
                    'sets': [{'weight': 40.0, 'reps': 10}],
                },
            ],
        }
        session = create_session(data)
        self.assertEqual(session.exercise_logs.count(), 2)
        first_log = session.exercise_logs.order_by('order_index').first()
        self.assertEqual(first_log.sets.count(), 2)

    def test_create_session_sets_order_index(self):
        data = {
            'date': '2026-03-22',
            'exercises': [
                {'exercise_id': self.exercise1.id, 'sets': [{'weight': 80.0, 'reps': 8}]},
                {'exercise_id': self.exercise2.id, 'sets': [{'weight': 40.0, 'reps': 10}]},
            ],
        }
        session = create_session(data)
        logs = list(session.exercise_logs.order_by('order_index'))
        self.assertEqual(logs[0].order_index, 0)
        self.assertEqual(logs[1].order_index, 1)

    def test_create_session_sets_set_number(self):
        data = {
            'date': '2026-03-22',
            'exercises': [
                {
                    'exercise_id': self.exercise1.id,
                    'sets': [{'weight': 80.0, 'reps': 8}, {'weight': 80.0, 'reps': 6}, {'weight': 75.0, 'reps': 6}],
                },
            ],
        }
        session = create_session(data)
        log = session.exercise_logs.first()
        set_numbers = list(log.sets.order_by('set_number').values_list('set_number', flat=True))
        self.assertEqual(set_numbers, [1, 2, 3])

    # Negative
    def test_create_session_missing_date(self):
        data = {
            'exercises': [
                {'exercise_id': self.exercise1.id, 'sets': [{'weight': 80.0, 'reps': 8}]},
            ],
        }
        with self.assertRaises(ValueError):
            create_session(data)

    def test_create_session_missing_exercises(self):
        data = {'date': '2026-03-22'}
        with self.assertRaises(ValueError):
            create_session(data)

    def test_create_session_invalid_exercise_id(self):
        data = {
            'date': '2026-03-22',
            'exercises': [
                {'exercise_id': 9999, 'sets': [{'weight': 80.0, 'reps': 8}]},
            ],
        }
        with self.assertRaises(ValueError):
            create_session(data)

    def test_create_session_empty_sets(self):
        data = {
            'date': '2026-03-22',
            'exercises': [
                {'exercise_id': self.exercise1.id, 'sets': []},
            ],
        }
        with self.assertRaises(ValueError):
            create_session(data)

    # Corner
    def test_create_session_single_exercise_single_set(self):
        data = {
            'date': '2026-03-22',
            'exercises': [
                {'exercise_id': self.exercise1.id, 'sets': [{'weight': 100.0, 'reps': 1}]},
            ],
        }
        session = create_session(data)
        self.assertEqual(session.exercise_logs.count(), 1)
        self.assertEqual(session.exercise_logs.first().sets.count(), 1)


# ── Serializer Tests ────────────────────────────────────────────────


class SessionSerializerTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')
        self.session = WorkoutSession.objects.create(date=date(2026, 3, 22))
        self.log = ExerciseLog.objects.create(session=self.session, exercise=self.exercise, order_index=0)
        SetLog.objects.create(exercise_log=self.log, set_number=1, weight=80.0, reps=8)
        SetLog.objects.create(exercise_log=self.log, set_number=2, weight=80.0, reps=6)

    # Positive
    def test_list_serializer_fields(self):
        data = SessionListSerializer(self.session).data
        self.assertEqual(data['id'], self.session.id)
        self.assertEqual(data['date'], '2026-03-22')
        self.assertIn('created_at', data)

    def test_detail_serializer_includes_exercises(self):
        data = SessionDetailSerializer(self.session).data
        self.assertIn('exercises', data)
        self.assertEqual(len(data['exercises']), 1)

    def test_detail_serializer_exercise_fields(self):
        data = SessionDetailSerializer(self.session).data
        ex = data['exercises'][0]
        self.assertEqual(ex['exercise_id'], self.exercise.id)
        self.assertEqual(ex['exercise_name'], 'Bench Press')
        self.assertIn('sets', ex)

    def test_detail_serializer_set_fields(self):
        data = SessionDetailSerializer(self.session).data
        s = data['exercises'][0]['sets'][0]
        self.assertEqual(s['weight'], 80.0)
        self.assertEqual(s['reps'], 8)

    # Corner

# ── View Tests ──────────────────────────────────────────────────────


class SessionListViewTest(TestCase):
    # Positive
    def test_list_sessions_200(self):
        response = self.client.get('/api/v1/sessions/')
        self.assertEqual(response.status_code, 200)

    def test_list_response_format(self):
        response = self.client.get('/api/v1/sessions/')
        data = response.json()
        self.assertIn('data', data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'success')

    # Corner
    def test_list_sessions_empty(self):
        response = self.client.get('/api/v1/sessions/')
        data = response.json()
        self.assertEqual(data['data'], [])
        self.assertEqual(data['message'], 'success')

    # Negative
    def test_list_delete_not_allowed(self):
        response = self.client.delete('/api/v1/sessions/')
        self.assertEqual(response.status_code, 405)


class SessionCreateViewTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')

    # Positive
    def test_create_session_201(self):
        payload = {
            'date': '2026-03-22',
            'exercises': [
                {
                    'exercise_id': self.exercise.id,
                    'sets': [{'weight': 80.0, 'reps': 8}],
                },
            ],
        }
        response = self.client.post('/api/v1/sessions/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_create_response_contains_id(self):
        payload = {
            'date': '2026-03-22',
            'exercises': [
                {
                    'exercise_id': self.exercise.id,
                    'sets': [{'weight': 80.0, 'reps': 8}],
                },
            ],
        }
        response = self.client.post('/api/v1/sessions/', data=json.dumps(payload), content_type='application/json')
        data = response.json()
        self.assertIn('id', data['data'])
        self.assertEqual(data['message'], 'success')

    # Negative
    def test_create_session_missing_date_400(self):
        payload = {
            'exercises': [
                {'exercise_id': self.exercise.id, 'sets': [{'weight': 80.0, 'reps': 8}]},
            ],
        }
        response = self.client.post('/api/v1/sessions/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_create_session_missing_exercises_400(self):
        payload = {'date': '2026-03-22'}
        response = self.client.post('/api/v1/sessions/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_create_session_invalid_exercise_id_400(self):
        payload = {
            'date': '2026-03-22',
            'exercises': [
                {'exercise_id': 9999, 'sets': [{'weight': 80.0, 'reps': 8}]},
            ],
        }
        response = self.client.post('/api/v1/sessions/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)


class SessionDetailViewTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')
        self.session = WorkoutSession.objects.create(date=date(2026, 3, 22))
        log = ExerciseLog.objects.create(session=self.session, exercise=self.exercise, order_index=0)
        SetLog.objects.create(exercise_log=log, set_number=1, weight=80.0, reps=8)

    # Positive
    def test_get_session_detail_200(self):
        response = self.client.get(f'/api/v1/sessions/{self.session.id}/')
        self.assertEqual(response.status_code, 200)

    def test_detail_response_contains_exercises(self):
        response = self.client.get(f'/api/v1/sessions/{self.session.id}/')
        data = response.json()['data']
        self.assertIn('exercises', data)
        self.assertEqual(len(data['exercises']), 1)

    def test_detail_response_contains_sets(self):
        response = self.client.get(f'/api/v1/sessions/{self.session.id}/')
        data = response.json()['data']
        sets = data['exercises'][0]['sets']
        self.assertEqual(len(sets), 1)
        self.assertEqual(sets[0]['weight'], 80.0)
        self.assertEqual(sets[0]['reps'], 8)

    # Negative
    def test_get_session_not_found_404(self):
        response = self.client.get('/api/v1/sessions/9999/')
        self.assertEqual(response.status_code, 404)

    def test_detail_post_not_allowed(self):
        response = self.client.post(f'/api/v1/sessions/{self.session.id}/')
        self.assertEqual(response.status_code, 405)


# ── Delete Session Tests ───────────────────────────────────────────


class DeleteSessionServiceTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')
        self.session = create_session(
            {
                'date': '2026-03-22',
                'exercises': [
                    {'exercise_id': self.exercise.id, 'sets': [{'weight': 80.0, 'reps': 8}]},
                ],
            }
        )

    def test_delete_session_removes_session(self):
        delete_session(self.session.id)
        self.assertEqual(WorkoutSession.objects.count(), 0)

    def test_delete_session_cascades_exercise_logs(self):
        delete_session(self.session.id)
        self.assertEqual(ExerciseLog.objects.count(), 0)

    def test_delete_session_cascades_set_logs(self):
        delete_session(self.session.id)
        self.assertEqual(SetLog.objects.count(), 0)

    def test_delete_session_not_found_raises(self):
        with self.assertRaises(WorkoutSession.DoesNotExist):
            delete_session(9999)


class DeleteSessionViewTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')
        self.session = create_session(
            {
                'date': '2026-03-22',
                'exercises': [
                    {'exercise_id': self.exercise.id, 'sets': [{'weight': 80.0, 'reps': 8}]},
                ],
            }
        )

    def test_delete_session_204(self):
        response = self.client.delete(f'/api/v1/sessions/{self.session.id}/')
        self.assertEqual(response.status_code, 204)

    def test_delete_session_actually_removes(self):
        self.client.delete(f'/api/v1/sessions/{self.session.id}/')
        self.assertEqual(WorkoutSession.objects.count(), 0)

    def test_delete_session_not_found_404(self):
        response = self.client.delete('/api/v1/sessions/9999/')
        self.assertEqual(response.status_code, 404)


# ── Update Session Tests ───────────────────────────────────────────


class UpdateSessionServiceTest(TestCase):
    def setUp(self):
        self.exercise1 = Exercise.objects.create(name='Bench Press', category='Push')
        self.exercise2 = Exercise.objects.create(name='Overhead Press', category='Push')
        self.session = create_session(
            {
                'date': '2026-03-22',
                'exercises': [
                    {'exercise_id': self.exercise1.id, 'sets': [{'weight': 80.0, 'reps': 8}]},
                ],
            }
        )

    def test_update_session_changes_date(self):
        session = update_session(
            self.session.id,
            {
                'date': '2026-03-25',
                'exercises': [
                    {'exercise_id': self.exercise1.id, 'sets': [{'weight': 80.0, 'reps': 8}]},
                ],
            },
        )
        self.assertEqual(session.date, date(2026, 3, 25))

    def test_update_session_replaces_exercises(self):
        update_session(
            self.session.id,
            {
                'date': '2026-03-22',
                'exercises': [
                    {'exercise_id': self.exercise2.id, 'sets': [{'weight': 40.0, 'reps': 10}]},
                ],
            },
        )
        logs = ExerciseLog.objects.filter(session=self.session)
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs.first().exercise_id, self.exercise2.id)

    def test_update_session_replaces_sets(self):
        update_session(
            self.session.id,
            {
                'date': '2026-03-22',
                'exercises': [
                    {
                        'exercise_id': self.exercise1.id,
                        'sets': [
                            {'weight': 85.0, 'reps': 6},
                            {'weight': 85.0, 'reps': 5},
                        ],
                    },
                ],
            },
        )
        log = ExerciseLog.objects.filter(session=self.session).first()
        self.assertEqual(log.sets.count(), 2)

    def test_update_session_not_found_raises(self):
        with self.assertRaises(WorkoutSession.DoesNotExist):
            update_session(
                9999,
                {
                    'date': '2026-03-22',
                    'exercises': [
                        {'exercise_id': self.exercise1.id, 'sets': [{'weight': 80.0, 'reps': 8}]},
                    ],
                },
            )

    def test_update_session_invalid_exercise_raises(self):
        with self.assertRaises(ValueError):
            update_session(
                self.session.id,
                {
                    'date': '2026-03-22',
                    'exercises': [
                        {'exercise_id': 9999, 'sets': [{'weight': 80.0, 'reps': 8}]},
                    ],
                },
            )


class UpdateSessionViewTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')
        self.session = create_session(
            {
                'date': '2026-03-22',
                'exercises': [
                    {'exercise_id': self.exercise.id, 'sets': [{'weight': 80.0, 'reps': 8}]},
                ],
            }
        )

    def test_update_session_200(self):
        payload = {
            'date': '2026-03-25',
            'exercises': [
                {'exercise_id': self.exercise.id, 'sets': [{'weight': 85.0, 'reps': 6}]},
            ],
        }
        response = self.client.put(
            f'/api/v1/sessions/{self.session.id}/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

    def test_update_response_contains_id(self):
        payload = {
            'date': '2026-03-25',
            'exercises': [
                {'exercise_id': self.exercise.id, 'sets': [{'weight': 85.0, 'reps': 6}]},
            ],
        }
        response = self.client.put(
            f'/api/v1/sessions/{self.session.id}/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        data = response.json()
        self.assertEqual(data['data']['id'], self.session.id)

    def test_update_session_not_found_404(self):
        payload = {
            'date': '2026-03-25',
            'exercises': [
                {'exercise_id': self.exercise.id, 'sets': [{'weight': 85.0, 'reps': 6}]},
            ],
        }
        response = self.client.put(
            '/api/v1/sessions/9999/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 404)

    def test_update_session_invalid_data_400(self):
        payload = {
            'date': '2026-03-25',
            'exercises': [
                {'exercise_id': 9999, 'sets': [{'weight': 85.0, 'reps': 6}]},
            ],
        }
        response = self.client.put(
            f'/api/v1/sessions/{self.session.id}/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
