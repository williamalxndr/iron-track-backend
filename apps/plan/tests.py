from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.exercise.models import Exercise
from apps.plan.models import Plan


class PlanApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='user1', password='testpass123')
        self.other_user = User.objects.create_user(username='user2', password='testpass123')
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

    def test_create_plan(self):
        resp = self.client.post(
            '/api/v1/plans/',
            {
                'name': 'New Plan',
                'type': 'PUSH',
                'exercises': [{'exercise_id': self.exercise.id, 'target_sets': 3, 'target_reps': 10}],
            },
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        plan = Plan.objects.get(id=resp.data['data']['id'])
        self.assertEqual(plan.user, self.user)
        self.assertFalse(plan.is_template)

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
