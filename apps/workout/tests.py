from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.exercise.models import Exercise
from apps.workout.models import WorkoutSession


class SessionApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='user1', password='testpass123')
        self.other_user = User.objects.create_user(username='user2', password='testpass123')
        self.exercise = Exercise.objects.create(name='Bench Press', category='Chest')
        self.client.force_authenticate(user=self.user)

    def _create_session(self, user=None):
        return WorkoutSession.objects.create(user=user or self.user, date=date.today())

    def test_list_sessions_only_own(self):
        self._create_session(self.user)
        self._create_session(self.other_user)
        resp = self.client.get('/api/v1/sessions/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data['data']), 1)

    def test_create_session(self):
        resp = self.client.post(
            '/api/v1/sessions/',
            {
                'date': '2025-01-15',
                'exercises': [
                    {
                        'exercise_id': self.exercise.id,
                        'sets': [{'weight': 60, 'reps': 10}],
                    },
                ],
            },
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WorkoutSession.objects.filter(user=self.user).exists())

    def test_get_session_detail(self):
        session = self._create_session()
        resp = self.client.get(f'/api/v1/sessions/{session.id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_other_users_session_returns_404(self):
        session = self._create_session(self.other_user)
        resp = self.client.get(f'/api/v1/sessions/{session.id}/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_session(self):
        session = self._create_session()
        resp = self.client.delete(f'/api/v1/sessions/{session.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(WorkoutSession.objects.filter(id=session.id).exists())

    def test_delete_other_users_session_returns_404(self):
        session = self._create_session(self.other_user)
        resp = self.client.delete(f'/api/v1/sessions/{session.id}/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(WorkoutSession.objects.filter(id=session.id).exists())

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        resp = self.client.get('/api/v1/sessions/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard(self):
        resp = self.client.get('/api/v1/sessions/dashboard/?timespan=1M')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('total_volume', resp.data['data'])
        self.assertIn('session_count', resp.data['data'])

    def test_dashboard_invalid_timespan(self):
        resp = self.client.get('/api/v1/sessions/dashboard/?timespan=1Y')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
