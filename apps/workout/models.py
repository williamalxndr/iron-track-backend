from django.db import models


class WorkoutSession(models.Model):
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workout_session'
        indexes = [
            models.Index(fields=['date'], name='idx_workout_session_date'),
        ]

    def __str__(self):
        return f'Session {self.date}'


class ExerciseLog(models.Model):
    session = models.ForeignKey(
        WorkoutSession,
        on_delete=models.CASCADE,
        related_name='exercise_logs',
    )
    exercise = models.ForeignKey(
        'exercise.Exercise',
        on_delete=models.CASCADE,
        related_name='exercise_logs',
    )
    order_index = models.IntegerField(default=0)

    class Meta:
        db_table = 'exercise_log'
        indexes = [
            models.Index(fields=['session'], name='idx_exercise_log_session'),
            models.Index(fields=['exercise'], name='idx_exercise_log_exercise'),
        ]

    def __str__(self):
        return f'{self.exercise.name} in {self.session}'


class SetLog(models.Model):
    exercise_log = models.ForeignKey(
        ExerciseLog,
        on_delete=models.CASCADE,
        related_name='sets',
    )
    set_number = models.IntegerField(null=True, blank=True)
    weight = models.FloatField()
    reps = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'set_log'
        indexes = [
            models.Index(fields=['exercise_log'], name='idx_set_log_exercise_log'),
        ]

    def __str__(self):
        return f'Set {self.set_number}: {self.weight}kg x {self.reps}'
