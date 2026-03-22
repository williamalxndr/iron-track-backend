from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exercise.models import Exercise
from apps.exercise.selectors import get_all_exercises, get_exercise_history, get_exercise_stats
from apps.exercise.serializers import ExerciseSerializer


class ExerciseListView(APIView):
    def get(self, request):
        exercises = get_all_exercises()
        serializer = ExerciseSerializer(exercises, many=True)
        return Response({'data': serializer.data, 'message': 'success'})


class ExerciseHistoryView(APIView):
    def get(self, request, pk):
        try:
            history = get_exercise_history(pk)
        except Exercise.DoesNotExist:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Exercise not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'data': history, 'message': 'success'})


class ExerciseStatsView(APIView):
    def get(self, request, pk):
        try:
            stats = get_exercise_stats(pk)
        except Exercise.DoesNotExist:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Exercise not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'data': stats, 'message': 'success'})
