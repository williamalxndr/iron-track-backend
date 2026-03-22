from django.db import models


class Exercise(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'exercise'

    def __str__(self):
        return self.name
