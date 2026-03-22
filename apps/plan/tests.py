from django.db import IntegrityError
from django.test import TestCase

from apps.exercise.models import Exercise
from apps.plan.models import Plan, PlanExercise, PlanWeekly, PlanWeeklyItem


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
