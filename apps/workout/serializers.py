from rest_framework import serializers

from apps.workout.models import ExerciseLog, SetLog, WorkoutSession


class SessionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutSession
        fields = ['id', 'date', 'notes', 'created_at']


class SetLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetLog
        fields = ['weight', 'reps']


class ExerciseLogDetailSerializer(serializers.ModelSerializer):
    exercise_id = serializers.IntegerField(source='exercise.id')
    exercise_name = serializers.CharField(source='exercise.name')
    sets = SetLogSerializer(many=True)

    class Meta:
        model = ExerciseLog
        fields = ['exercise_id', 'exercise_name', 'sets']


class SessionDetailSerializer(serializers.ModelSerializer):
    exercises = ExerciseLogDetailSerializer(source='exercise_logs', many=True)

    class Meta:
        model = WorkoutSession
        fields = ['id', 'date', 'notes', 'exercises']
