from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exercise.selectors import get_all_exercises
from apps.exercise.serializers import ExerciseSerializer


class ExerciseListView(APIView):
    def get(self, request):
        exercises = get_all_exercises()
        serializer = ExerciseSerializer(exercises, many=True)
        return Response({'data': serializer.data, 'message': 'success'})
