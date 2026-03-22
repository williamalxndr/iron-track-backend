from django.db import models


class Plan(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20)  # PUSH / PULL / LEG / FULL_BODY

    class Meta:
        db_table = 'plan'

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
    target_sets = models.IntegerField(null=True, blank=True)
    target_reps = models.IntegerField(null=True, blank=True)
    order_index = models.IntegerField(default=0)

    class Meta:
        db_table = 'plan_exercise'
        indexes = [
            models.Index(fields=['plan'], name='idx_plan_exercise_plan'),
        ]

    def __str__(self):
        return f"{self.exercise.name} in {self.plan.name}"


class PlanWeekly(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'plan_weekly'

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
        return f"Day {self.day_of_week}: {self.plan.name}"
