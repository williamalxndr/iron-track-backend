from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .selectors import get_all_exercises, get_exercise_history, get_exercise_stats
from .serializers import ExerciseSerializer


class ExerciseListView(APIView):
    def get(self, request):
        exercises = get_all_exercises()
        data = ExerciseSerializer(exercises, many=True).data
        return Response({'data': data, 'message': 'success'})


class ExerciseHistoryView(APIView):
    def get(self, request, pk):
        try:
            history = get_exercise_history(pk, user=request.user)
        except Exception:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Exercise not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'data': history, 'message': 'success'})


class ExerciseStatsView(APIView):
    def get(self, request, pk):
        try:
            stats = get_exercise_stats(pk, user=request.user)
        except Exception:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Exercise not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'data': stats, 'message': 'success'})
