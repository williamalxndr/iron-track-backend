from rest_framework import serializers

from apps.exercise.models import Exercise


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'category', 'created_at']
