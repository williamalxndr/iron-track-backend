from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.workout.models import WorkoutSession
from apps.workout.selectors import get_all_sessions, get_dashboard_stats, get_session_by_id
from apps.workout.serializers import SessionDetailSerializer, SessionListSerializer
from apps.workout.services import create_session, delete_session, update_session


class DashboardView(APIView):
    def get(self, request):
        timespan = request.query_params.get('timespan', '1M')
        if timespan not in ('1W', '1M', '3M'):
            return Response(
                {'error': {'code': 'INVALID_REQUEST', 'message': 'timespan must be 1W, 1M, or 3M'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        stats = get_dashboard_stats(timespan)
        return Response({'data': stats, 'message': 'success'})


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

    def put(self, request, pk):
        try:
            session = update_session(pk, request.data)
        except WorkoutSession.DoesNotExist:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Session not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValueError as e:
            return Response(
                {'error': {'code': 'INVALID_REQUEST', 'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'data': {'id': session.id}, 'message': 'success'})

    def delete(self, request, pk):
        try:
            delete_session(pk)
        except WorkoutSession.DoesNotExist:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Session not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
