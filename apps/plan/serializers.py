from rest_framework import serializers

from .models import Plan, PlanExercise, PlanWeekly, PlanWeeklyItem


class PlanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'type', 'is_template']


class PlanExerciseDetailSerializer(serializers.ModelSerializer):
    exercise_id = serializers.IntegerField(source='exercise.id')
    exercise_name = serializers.CharField(source='exercise.name')

    class Meta:
        model = PlanExercise
        fields = ['exercise_id', 'exercise_name', 'order_index']


class PlanDetailSerializer(serializers.ModelSerializer):
    exercises = PlanExerciseDetailSerializer(many=True)

    class Meta:
        model = Plan
        fields = ['id', 'name', 'type', 'is_template', 'exercises']


class PlanWeeklyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanWeekly
        fields = ['id', 'name', 'is_template']


class PlanWeeklyItemSerializer(serializers.ModelSerializer):
    plan_id = serializers.IntegerField(source='plan.id')
    plan_name = serializers.CharField(source='plan.name')

    class Meta:
        model = PlanWeeklyItem
        fields = ['plan_id', 'plan_name', 'day_of_week']


class PlanWeeklyDetailSerializer(serializers.ModelSerializer):
    items = PlanWeeklyItemSerializer(many=True)

    class Meta:
        model = PlanWeekly
        fields = ['id', 'name', 'is_template', 'items']
