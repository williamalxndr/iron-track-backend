from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.workout.models import WorkoutSession
from apps.workout.selectors import get_all_sessions, get_session_by_id
from apps.workout.serializers import SessionDetailSerializer, SessionListSerializer
from apps.workout.services import create_session


class SessionListView(APIView):
    def get(self, request):
        sessions = get_all_sessions()
        serializer = SessionListSerializer(sessions, many=True)
        return Response({'data': serializer.data, 'message': 'success'})

    def post(self, request):
        try:
            session = create_session(request.data)
        except ValueError as e:
            return Response(
                {'error': {'code': 'INVALID_REQUEST', 'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'data': {'id': session.id}, 'message': 'success'}, status=status.HTTP_201_CREATED)


class SessionDetailView(APIView):
    def get(self, request, pk):
        try:
            session = get_session_by_id(pk)
        except WorkoutSession.DoesNotExist:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Session not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = SessionDetailSerializer(session)
        return Response({'data': serializer.data, 'message': 'success'})
