import json

from django.db import IntegrityError
from django.db.models import QuerySet
from django.test import TestCase

from apps.exercise.models import Exercise
from apps.plan.models import Plan, PlanExercise, PlanWeekly, PlanWeeklyItem
from apps.plan.selectors import (
    get_all_plan_weeklies,
    get_all_plans,
    get_plan_by_id,
    get_plan_weekly_by_id,
)
from apps.plan.serializers import (
    PlanDetailSerializer,
    PlanListSerializer,
    PlanWeeklyDetailSerializer,
    PlanWeeklyListSerializer,
)
from apps.plan.services import create_plan


class PlanModelTest(TestCase):
    def test_create_plan(self):
        plan = Plan.objects.create(name='Push Day', type='PUSH')
        self.assertEqual(plan.name, 'Push Day')
        self.assertEqual(plan.type, 'PUSH')

    def test_name_is_required(self):
        with self.assertRaises(IntegrityError):
            Plan.objects.create(name=None, type='PUSH')

    def test_type_is_required(self):
        with self.assertRaises(IntegrityError):
            Plan.objects.create(name='Leg Day', type=None)

    def test_str(self):
        plan = Plan.objects.create(name='Pull Day', type='PULL')
        self.assertEqual(str(plan), 'Pull Day')

    def test_db_table_name(self):
        self.assertEqual(Plan._meta.db_table, 'plan')


class PlanExerciseModelTest(TestCase):
    def setUp(self):
        self.plan = Plan.objects.create(name='Push Day', type='PUSH')
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')

    def test_create_plan_exercise(self):
        pe = PlanExercise.objects.create(
            plan=self.plan,
            exercise=self.exercise,
            target_sets=3,
            target_reps=10,
        )
        self.assertEqual(pe.plan, self.plan)
        self.assertEqual(pe.exercise, self.exercise)
        self.assertEqual(pe.target_sets, 3)
        self.assertEqual(pe.target_reps, 10)

    def test_target_sets_and_reps_optional(self):
        pe = PlanExercise.objects.create(plan=self.plan, exercise=self.exercise)
        self.assertIsNone(pe.target_sets)
        self.assertIsNone(pe.target_reps)

    def test_order_index_default(self):
        pe = PlanExercise.objects.create(plan=self.plan, exercise=self.exercise)
        self.assertEqual(pe.order_index, 0)

    def test_cascade_delete_plan(self):
        PlanExercise.objects.create(plan=self.plan, exercise=self.exercise)
        self.plan.delete()
        self.assertEqual(PlanExercise.objects.count(), 0)

    def test_cascade_delete_exercise(self):
        PlanExercise.objects.create(plan=self.plan, exercise=self.exercise)
        self.exercise.delete()
        self.assertEqual(PlanExercise.objects.count(), 0)

    def test_str(self):
        pe = PlanExercise.objects.create(plan=self.plan, exercise=self.exercise)
        self.assertEqual(str(pe), 'Bench Press in Push Day')

    def test_db_table_name(self):
        self.assertEqual(PlanExercise._meta.db_table, 'plan_exercise')


class PlanWeeklyModelTest(TestCase):
    def test_create_plan_weekly(self):
        pw = PlanWeekly.objects.create(name='PPL')
        self.assertEqual(pw.name, 'PPL')

    def test_str(self):
        pw = PlanWeekly.objects.create(name='Upper Lower')
        self.assertEqual(str(pw), 'Upper Lower')

    def test_db_table_name(self):
        self.assertEqual(PlanWeekly._meta.db_table, 'plan_weekly')


class PlanWeeklyItemModelTest(TestCase):
    def setUp(self):
        self.plan = Plan.objects.create(name='Push Day', type='PUSH')
        self.weekly = PlanWeekly.objects.create(name='PPL')

    def test_create_plan_weekly_item(self):
        item = PlanWeeklyItem.objects.create(
            plan_weekly=self.weekly,
            plan=self.plan,
            day_of_week=1,
        )
        self.assertEqual(item.day_of_week, 1)
        self.assertEqual(item.plan, self.plan)
        self.assertEqual(item.plan_weekly, self.weekly)

    def test_day_of_week_min_boundary(self):
        item = PlanWeeklyItem.objects.create(plan_weekly=self.weekly, plan=self.plan, day_of_week=1)
        self.assertEqual(item.day_of_week, 1)

    def test_day_of_week_max_boundary(self):
        item = PlanWeeklyItem.objects.create(plan_weekly=self.weekly, plan=self.plan, day_of_week=7)
        self.assertEqual(item.day_of_week, 7)

    def test_cascade_delete_plan_weekly(self):
        PlanWeeklyItem.objects.create(plan_weekly=self.weekly, plan=self.plan, day_of_week=1)
        self.weekly.delete()
        self.assertEqual(PlanWeeklyItem.objects.count(), 0)

    def test_cascade_delete_plan(self):
        PlanWeeklyItem.objects.create(plan_weekly=self.weekly, plan=self.plan, day_of_week=1)
        self.plan.delete()
        self.assertEqual(PlanWeeklyItem.objects.count(), 0)

    def test_str(self):
        item = PlanWeeklyItem.objects.create(plan_weekly=self.weekly, plan=self.plan, day_of_week=3)
        self.assertEqual(str(item), 'Day 3: Push Day')

    def test_db_table_name(self):
        self.assertEqual(PlanWeeklyItem._meta.db_table, 'plan_weekly_item')


# ── Selector Tests ──────────────────────────────────────────────────


class PlanSelectorTest(TestCase):
    # Positive
    def test_get_all_plans_returns_queryset(self):
        result = get_all_plans()
        self.assertIsInstance(result, QuerySet)

    def test_get_all_plans_returns_all(self):
        Plan.objects.create(name='Push Day', type='PUSH')
        Plan.objects.create(name='Pull Day', type='PULL')
        result = get_all_plans()
        self.assertEqual(result.count(), 2)

    # Corner
    def test_get_all_plans_empty(self):
        result = get_all_plans()
        self.assertEqual(result.count(), 0)

    # Positive
    def test_get_plan_by_id_returns_plan(self):
        plan = Plan.objects.create(name='Push Day', type='PUSH')
        result = get_plan_by_id(plan.id)
        self.assertEqual(result.id, plan.id)

    # Negative
    def test_get_plan_by_id_not_found_raises(self):
        with self.assertRaises(Plan.DoesNotExist):
            get_plan_by_id(9999)


# ── Service Tests ───────────────────────────────────────────────────


class PlanServiceTest(TestCase):
    def setUp(self):
        self.exercise1 = Exercise.objects.create(name='Bench Press', category='Push')
        self.exercise2 = Exercise.objects.create(name='Overhead Press', category='Push')

    # Positive
    def test_create_plan_basic(self):
        data = {'name': 'Push Day', 'type': 'PUSH', 'exercises': []}
        plan = create_plan(data)
        self.assertEqual(plan.name, 'Push Day')
        self.assertEqual(plan.type, 'PUSH')

    def test_create_plan_with_exercises(self):
        data = {
            'name': 'Push Day',
            'type': 'PUSH',
            'exercises': [
                {'exercise_id': self.exercise1.id, 'target_sets': 3, 'target_reps': 10},
                {'exercise_id': self.exercise2.id, 'target_sets': 3, 'target_reps': 8},
            ],
        }
        plan = create_plan(data)
        self.assertEqual(plan.exercises.count(), 2)

    def test_create_plan_without_exercises(self):
        data = {'name': 'Push Day', 'type': 'PUSH'}
        plan = create_plan(data)
        self.assertEqual(plan.exercises.count(), 0)

    def test_create_plan_sets_order_index(self):
        data = {
            'name': 'Push Day',
            'type': 'PUSH',
            'exercises': [
                {'exercise_id': self.exercise1.id, 'target_sets': 3, 'target_reps': 10},
                {'exercise_id': self.exercise2.id, 'target_sets': 3, 'target_reps': 8},
            ],
        }
        plan = create_plan(data)
        exercises = list(plan.exercises.order_by('order_index'))
        self.assertEqual(exercises[0].order_index, 0)
        self.assertEqual(exercises[1].order_index, 1)

    # Negative
    def test_create_plan_missing_name(self):
        data = {'type': 'PUSH'}
        with self.assertRaises(ValueError):
            create_plan(data)

    def test_create_plan_missing_type(self):
        data = {'name': 'Push Day'}
        with self.assertRaises(ValueError):
            create_plan(data)

    def test_create_plan_invalid_exercise_id(self):
        data = {
            'name': 'Push Day',
            'type': 'PUSH',
            'exercises': [{'exercise_id': 9999, 'target_sets': 3, 'target_reps': 10}],
        }
        with self.assertRaises(ValueError):
            create_plan(data)

    # Corner
    def test_create_plan_single_exercise(self):
        data = {
            'name': 'Push Day',
            'type': 'PUSH',
            'exercises': [{'exercise_id': self.exercise1.id, 'target_sets': 5, 'target_reps': 5}],
        }
        plan = create_plan(data)
        self.assertEqual(plan.exercises.count(), 1)


# ── Serializer Tests ────────────────────────────────────────────────


class PlanSerializerTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')
        self.plan = Plan.objects.create(name='Push Day', type='PUSH')
        PlanExercise.objects.create(
            plan=self.plan, exercise=self.exercise, target_sets=3, target_reps=10, order_index=0
        )

    # Positive
    def test_list_serializer_fields(self):
        data = PlanListSerializer(self.plan).data
        self.assertEqual(data['id'], self.plan.id)
        self.assertEqual(data['name'], 'Push Day')
        self.assertEqual(data['type'], 'PUSH')

    def test_detail_serializer_includes_exercises(self):
        data = PlanDetailSerializer(self.plan).data
        self.assertIn('exercises', data)
        self.assertEqual(len(data['exercises']), 1)

    def test_detail_serializer_exercise_fields(self):
        data = PlanDetailSerializer(self.plan).data
        ex = data['exercises'][0]
        self.assertEqual(ex['exercise_id'], self.exercise.id)
        self.assertEqual(ex['exercise_name'], 'Bench Press')
        self.assertEqual(ex['target_sets'], 3)
        self.assertEqual(ex['target_reps'], 10)

    # Corner
    def test_detail_serializer_null_targets(self):
        plan = Plan.objects.create(name='Flex Day', type='FULL_BODY')
        PlanExercise.objects.create(plan=plan, exercise=self.exercise, order_index=0)
        data = PlanDetailSerializer(plan).data
        ex = data['exercises'][0]
        self.assertIsNone(ex['target_sets'])
        self.assertIsNone(ex['target_reps'])


# ── View Tests ──────────────────────────────────────────────────────


class PlanListViewTest(TestCase):
    # Positive
    def test_list_plans_200(self):
        response = self.client.get('/api/v1/plans/')
        self.assertEqual(response.status_code, 200)

    def test_list_response_format(self):
        response = self.client.get('/api/v1/plans/')
        data = response.json()
        self.assertIn('data', data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'success')

    # Corner
    def test_list_plans_empty(self):
        response = self.client.get('/api/v1/plans/')
        data = response.json()
        self.assertEqual(data['data'], [])

    # Negative
    def test_list_delete_not_allowed_405(self):
        response = self.client.delete('/api/v1/plans/')
        self.assertEqual(response.status_code, 405)


class PlanCreateViewTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')

    # Positive
    def test_create_plan_201(self):
        payload = {
            'name': 'Push Day',
            'type': 'PUSH',
            'exercises': [{'exercise_id': self.exercise.id, 'target_sets': 3, 'target_reps': 10}],
        }
        response = self.client.post('/api/v1/plans/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_create_response_contains_id(self):
        payload = {'name': 'Push Day', 'type': 'PUSH'}
        response = self.client.post('/api/v1/plans/', data=json.dumps(payload), content_type='application/json')
        data = response.json()
        self.assertIn('id', data['data'])
        self.assertEqual(data['message'], 'success')

    # Negative
    def test_create_plan_missing_name_400(self):
        payload = {'type': 'PUSH'}
        response = self.client.post('/api/v1/plans/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_create_plan_missing_type_400(self):
        payload = {'name': 'Push Day'}
        response = self.client.post('/api/v1/plans/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)


class PlanDetailViewTest(TestCase):
    def setUp(self):
        self.exercise = Exercise.objects.create(name='Bench Press', category='Push')
        self.plan = Plan.objects.create(name='Push Day', type='PUSH')
        PlanExercise.objects.create(
            plan=self.plan, exercise=self.exercise, target_sets=3, target_reps=10, order_index=0
        )

    # Positive
    def test_get_plan_detail_200(self):
        response = self.client.get(f'/api/v1/plans/{self.plan.id}/')
        self.assertEqual(response.status_code, 200)

    def test_detail_response_contains_exercises(self):
        response = self.client.get(f'/api/v1/plans/{self.plan.id}/')
        data = response.json()['data']
        self.assertIn('exercises', data)
        self.assertEqual(len(data['exercises']), 1)

    # Negative
    def test_get_plan_not_found_404(self):
        response = self.client.get('/api/v1/plans/9999/')
        self.assertEqual(response.status_code, 404)

    def test_detail_post_not_allowed_405(self):
        response = self.client.post(f'/api/v1/plans/{self.plan.id}/')
        self.assertEqual(response.status_code, 405)


# ── Plan Weekly Selector Tests ─────────────────────────────────────


class PlanWeeklySelectorTest(TestCase):
    # Positive
    def test_get_all_plan_weeklies_returns_queryset(self):
        result = get_all_plan_weeklies()
        self.assertIsInstance(result, QuerySet)

    def test_get_all_plan_weeklies_returns_all(self):
        PlanWeekly.objects.create(name='PPL')
        PlanWeekly.objects.create(name='Upper Lower')
        result = get_all_plan_weeklies()
        self.assertEqual(result.count(), 2)

    # Corner
    def test_get_all_plan_weeklies_empty(self):
        result = get_all_plan_weeklies()
        self.assertEqual(result.count(), 0)

    # Positive
    def test_get_plan_weekly_by_id_returns_plan_weekly(self):
        pw = PlanWeekly.objects.create(name='PPL')
        result = get_plan_weekly_by_id(pw.id)
        self.assertEqual(result.id, pw.id)

    # Negative
    def test_get_plan_weekly_by_id_not_found_raises(self):
        with self.assertRaises(PlanWeekly.DoesNotExist):
            get_plan_weekly_by_id(9999)


# ── Plan Weekly Serializer Tests ───────────────────────────────────


class PlanWeeklySerializerTest(TestCase):
    def setUp(self):
        self.plan = Plan.objects.create(name='Push Day', type='PUSH')
        self.weekly = PlanWeekly.objects.create(name='PPL')
        PlanWeeklyItem.objects.create(plan_weekly=self.weekly, plan=self.plan, day_of_week=1)

    # Positive
    def test_list_serializer_fields(self):
        data = PlanWeeklyListSerializer(self.weekly).data
        self.assertEqual(data['id'], self.weekly.id)
        self.assertEqual(data['name'], 'PPL')

    def test_detail_serializer_includes_items(self):
        data = PlanWeeklyDetailSerializer(self.weekly).data
        self.assertIn('items', data)
        self.assertEqual(len(data['items']), 1)

    def test_detail_serializer_item_fields(self):
        data = PlanWeeklyDetailSerializer(self.weekly).data
        item = data['items'][0]
        self.assertEqual(item['day_of_week'], 1)
        self.assertEqual(item['plan_id'], self.plan.id)
        self.assertEqual(item['plan_name'], 'Push Day')

    # Corner
    def test_detail_serializer_no_items(self):
        empty_weekly = PlanWeekly.objects.create(name='Empty Week')
        data = PlanWeeklyDetailSerializer(empty_weekly).data
        self.assertEqual(data['items'], [])


# ── Plan Weekly View Tests ─────────────────────────────────────────


class PlanWeeklyListViewTest(TestCase):
    # Positive
    def test_list_plan_weeklies_200(self):
        response = self.client.get('/api/v1/plan-weekly/')
        self.assertEqual(response.status_code, 200)

    def test_list_response_format(self):
        response = self.client.get('/api/v1/plan-weekly/')
        data = response.json()
        self.assertIn('data', data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'success')

    # Corner
    def test_list_plan_weeklies_empty(self):
        response = self.client.get('/api/v1/plan-weekly/')
        data = response.json()
        self.assertEqual(data['data'], [])

    # Negative
    def test_list_post_not_allowed_405(self):
        response = self.client.post('/api/v1/plan-weekly/')
        self.assertEqual(response.status_code, 405)


class PlanWeeklyDetailViewTest(TestCase):
    def setUp(self):
        self.plan = Plan.objects.create(name='Push Day', type='PUSH')
        self.weekly = PlanWeekly.objects.create(name='PPL')
        PlanWeeklyItem.objects.create(plan_weekly=self.weekly, plan=self.plan, day_of_week=1)

    # Positive
    def test_get_plan_weekly_detail_200(self):
        response = self.client.get(f'/api/v1/plan-weekly/{self.weekly.id}/')
        self.assertEqual(response.status_code, 200)

    def test_detail_response_contains_items(self):
        response = self.client.get(f'/api/v1/plan-weekly/{self.weekly.id}/')
        data = response.json()['data']
        self.assertIn('items', data)
        self.assertEqual(len(data['items']), 1)

    # Negative
    def test_get_plan_weekly_not_found_404(self):
        response = self.client.get('/api/v1/plan-weekly/9999/')
        self.assertEqual(response.status_code, 404)

    def test_detail_post_not_allowed_405(self):
        response = self.client.post(f'/api/v1/plan-weekly/{self.weekly.id}/')
        self.assertEqual(response.status_code, 405)
