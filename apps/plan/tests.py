from django.test import TestCase  # type: ignore
from rest_framework import status  # type: ignore
from rest_framework.test import APIClient  # type: ignore

from apps.accounts.models import User  # type: ignore
from apps.exercise.models import Exercise  # type: ignore
from apps.plan.models import Plan  # type: ignore

TEST_PASSWORD = 'testpass123'  # noqa: S105


class PlanApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='user1', password=TEST_PASSWORD)
        self.other_user = User.objects.create_user(username='user2', password=TEST_PASSWORD)
        self.exercise = Exercise.objects.create(name='Squat', category='Quads')
        self.client.force_authenticate(user=self.user)

    def test_list_plans_includes_templates_and_own(self):
        Plan.objects.create(name='Template', type='PUSH', is_template=True, user=None)
        Plan.objects.create(name='My Plan', type='PULL', is_template=False, user=self.user)
        Plan.objects.create(name='Other Plan', type='LEG', is_template=False, user=self.other_user)
        resp = self.client.get('/api/v1/plans/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        names = [p['name'] for p in resp.data['data']]
        self.assertIn('Template', names)
        self.assertIn('My Plan', names)
        self.assertNotIn('Other Plan', names)

    def test_create_plan_no_name_returns_400(self):
        resp = self.client.post('/api/v1/plans/', {'type': 'PUSH', 'exercises': []}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_plan_invalid_exercise_returns_400(self):
        resp = self.client.post(
            '/api/v1/plans/',
            {'name': 'Fail', 'type': 'PUSH', 'exercises': [{'exercise_id': 9999}]},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_plan(self):
        plan = Plan.objects.create(name='Old', type='PUSH', user=self.user)
        resp = self.client.put(
            f'/api/v1/plans/{plan.id}/',
            {'name': 'Updated', 'type': 'PULL', 'exercises': []},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        plan.refresh_from_db()
        self.assertEqual(plan.name, 'Updated')

    def test_delete_plan(self):
        plan = Plan.objects.create(name='Delete me', type='PUSH', user=self.user)
        resp = self.client.delete(f'/api/v1/plans/{plan.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Plan.objects.filter(id=plan.id).exists())

    def test_cannot_edit_template_plan(self):
        template = Plan.objects.create(name='Template', type='PUSH', is_template=True, user=None)
        resp = self.client.put(
            f'/api/v1/plans/{template.id}/',
            {
                'name': 'Hacked',
                'type': 'PUSH',
                'exercises': [],
            },
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_template_plan(self):
        template = Plan.objects.create(name='Template', type='PUSH', is_template=True, user=None)
        resp = self.client.delete(f'/api/v1/plans/{template.id}/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Plan.objects.filter(id=template.id).exists())

    def test_cannot_edit_other_users_plan(self):
        other_plan = Plan.objects.create(name='Other', type='PUSH', is_template=False, user=self.other_user)
        resp = self.client.put(
            f'/api/v1/plans/{other_plan.id}/',
            {
                'name': 'Hacked',
                'type': 'PUSH',
                'exercises': [],
            },
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_other_users_plan(self):
        other_plan = Plan.objects.create(name='Other', type='PUSH', is_template=False, user=self.other_user)
        resp = self.client.delete(f'/api/v1/plans/{other_plan.id}/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_template_plan_detail(self):
        template = Plan.objects.create(name='Template', type='PUSH', is_template=True, user=None)
        resp = self.client.get(f'/api/v1/plans/{template.id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['data']['name'], 'Template')

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        resp = self.client.get('/api/v1/plans/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
