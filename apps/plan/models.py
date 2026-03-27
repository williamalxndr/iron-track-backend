from django.conf import settings
from django.db import models


class Plan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='plans',
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20)  # PUSH / PULL / LEG / FULL_BODY
    is_template = models.BooleanField(default=False)

    class Meta:
        db_table = 'plan'
        indexes = [
            models.Index(fields=['user'], name='idx_plan_user'),
        ]

    def __str__(self):
        return self.name


class PlanExercise(models.Model):
    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name='exercises',
    )
    exercise = models.ForeignKey(
        'exercise.Exercise',
        on_delete=models.CASCADE,
        related_name='plan_exercises',
    )
    order_index = models.IntegerField(default=0)

    class Meta:
        db_table = 'plan_exercise'
        indexes = [
            models.Index(fields=['plan'], name='idx_plan_exercise_plan'),
        ]

    def __str__(self):
        return f'{self.exercise.name} in {self.plan.name}'


class PlanWeekly(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='weekly_plans',
    )
    name = models.CharField(max_length=255)
    is_template = models.BooleanField(default=False)

    class Meta:
        db_table = 'plan_weekly'
        indexes = [
            models.Index(fields=['user'], name='idx_plan_weekly_user'),
        ]

    def __str__(self):
        return self.name


class PlanWeeklyItem(models.Model):
    plan_weekly = models.ForeignKey(
        PlanWeekly,
        on_delete=models.CASCADE,
        related_name='items',
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name='weekly_items',
    )
    day_of_week = models.IntegerField()  # 1-7

    class Meta:
        db_table = 'plan_weekly_item'
        indexes = [
            models.Index(fields=['plan_weekly'], name='idx_plan_weekly_item_weekly'),
            models.Index(fields=['day_of_week'], name='idx_plan_weekly_item_day'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(day_of_week__gte=1, day_of_week__lte=7),
                name='chk_day_of_week',
            ),
        ]

    def __str__(self):
        return f'Day {self.day_of_week}: {self.plan.name}'
