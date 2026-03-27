from datetime import date

from django.test import TestCase  # type: ignore
from rest_framework import status  # type: ignore
from rest_framework.test import APIClient  # type: ignore

from apps.accounts.models import User  # type: ignore
from apps.exercise.models import Exercise  # type: ignore
from apps.workout.models import WorkoutSession  # type: ignore

TEST_PASSWORD = 'testpass123'  # noqa: S105


class SessionApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='user1', password=TEST_PASSWORD)
        self.other_user = User.objects.create_user(username='user2', password=TEST_PASSWORD)
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

    def test_create_session_no_date_uses_today(self):
        resp = self.client.post(
            '/api/v1/sessions/',
            {'exercises': [{'exercise_id': self.exercise.id, 'sets': [{'weight': 60, 'reps': 10}]}]},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkoutSession.objects.first().date, date.today())

    def test_create_session_invalid_exercise_returns_400(self):
        resp = self.client.post(
            '/api/v1/sessions/',
            {'date': '2025-01-15', 'exercises': [{'exercise_id': 9999, 'sets': [{'weight': 60, 'reps': 10}]}]},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_session_no_sets_returns_400(self):
        resp = self.client.post(
            '/api/v1/sessions/',
            {'date': '2025-01-15', 'exercises': [{'exercise_id': self.exercise.id, 'sets': []}]},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_session(self):
        session = self._create_session()
        resp = self.client.put(
            f'/api/v1/sessions/{session.id}/',
            {
                'date': '2025-01-20',
                'exercises': [{'exercise_id': self.exercise.id, 'sets': [{'weight': 70, 'reps': 5}]}],
            },
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        session.refresh_from_db()
        self.assertEqual(session.date, date(2025, 1, 20))

    def test_update_other_users_session_returns_404(self):
        session = self._create_session(self.other_user)
        resp = self.client.put(
            f'/api/v1/sessions/{session.id}/',
            {
                'date': '2025-01-20',
                'exercises': [{'exercise_id': self.exercise.id, 'sets': [{'weight': 70, 'reps': 5}]}],
            },
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

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
