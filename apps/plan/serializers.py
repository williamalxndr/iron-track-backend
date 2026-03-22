from rest_framework import serializers

from apps.plan.models import Plan, PlanExercise


class PlanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'type']


class PlanExerciseDetailSerializer(serializers.ModelSerializer):
    exercise_id = serializers.IntegerField(source='exercise.id')
    exercise_name = serializers.CharField(source='exercise.name')

    class Meta:
        model = PlanExercise
        fields = ['exercise_id', 'exercise_name', 'target_sets', 'target_reps']


class PlanDetailSerializer(serializers.ModelSerializer):
    exercises = PlanExerciseDetailSerializer(many=True)

    class Meta:
        model = Plan
        fields = ['id', 'name', 'type', 'exercises']
