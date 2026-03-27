from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.exercise.models import Exercise
from apps.workout.models import ExerciseLog, SetLog, WorkoutSession

TEST_PASSWORD = 'testpass123'  # noqa: S105


class ExerciseApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='user1', password=TEST_PASSWORD)
        self.other_user = User.objects.create_user(username='user2', password=TEST_PASSWORD)
        self.exercise = Exercise.objects.create(name='Bench Press', category='Chest')
        self.client.force_authenticate(user=self.user)

    def test_list_exercises(self):
        resp = self.client.get('/api/v1/exercises/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['data']), 1)

    def test_exercise_history_only_own_sessions(self):
        for u in [self.user, self.other_user]:
            session = WorkoutSession.objects.create(user=u, date=date.today())
            log = ExerciseLog.objects.create(session=session, exercise=self.exercise, order_index=0)
            SetLog.objects.create(exercise_log=log, set_number=1, weight=60, reps=10)

        resp = self.client.get(f'/api/v1/exercises/{self.exercise.id}/history/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['data']), 1)

    def test_exercise_stats_only_own_sessions(self):
        session = WorkoutSession.objects.create(user=self.user, date=date.today())
        log = ExerciseLog.objects.create(session=session, exercise=self.exercise, order_index=0)
        SetLog.objects.create(exercise_log=log, set_number=1, weight=100, reps=5)

        resp = self.client.get(f'/api/v1/exercises/{self.exercise.id}/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('max_weight', resp.data['data'])

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        resp = self.client.get('/api/v1/exercises/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
