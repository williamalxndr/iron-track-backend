from rest_framework import serializers

from apps.plan.models import Plan, PlanExercise, PlanWeekly, PlanWeeklyItem


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


class PlanWeeklyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanWeekly
        fields = ['id', 'name']


class PlanWeeklyItemSerializer(serializers.ModelSerializer):
    plan_id = serializers.IntegerField(source='plan.id')
    plan_name = serializers.CharField(source='plan.name')

    class Meta:
        model = PlanWeeklyItem
        fields = ['day_of_week', 'plan_id', 'plan_name']


class PlanWeeklyDetailSerializer(serializers.ModelSerializer):
    items = PlanWeeklyItemSerializer(many=True)

    class Meta:
        model = PlanWeekly
        fields = ['id', 'name', 'items']
