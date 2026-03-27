from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .selectors import get_all_sessions, get_dashboard_stats, get_session_by_id
from .serializers import SessionDetailSerializer, SessionListSerializer
from .services import create_session, delete_session, update_session


class SessionListView(APIView):
    def get(self, request):
        sessions = get_all_sessions(user=request.user)
        data = SessionListSerializer(sessions, many=True).data
        return Response({'data': data, 'message': 'success'})

    def post(self, request):
        try:
            session = create_session(request.data, user=request.user)
        except ValueError as e:
            return Response(
                {'error': {'code': 'INVALID_REQUEST', 'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {'data': {'id': session.id}, 'message': 'success'},
            status=status.HTTP_201_CREATED,
        )


class SessionDetailView(APIView):
    def get(self, request, pk):
        try:
            session = get_session_by_id(pk, user=request.user)
        except Exception:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Session not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = SessionDetailSerializer(session).data
        return Response({'data': data, 'message': 'success'})

    def put(self, request, pk):
        try:
            update_session(pk, request.data, user=request.user)
        except ValueError as e:
            return Response(
                {'error': {'code': 'INVALID_REQUEST', 'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Session not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'data': None, 'message': 'success'})

    def delete(self, request, pk):
        try:
            delete_session(pk, user=request.user)
        except Exception:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Session not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardView(APIView):
    def get(self, request):
        timespan = request.query_params.get('timespan', '1M')
        if timespan not in ('1W', '1M', '3M'):
            return Response(
                {'error': {'code': 'INVALID_REQUEST', 'message': 'Invalid timespan'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        stats = get_dashboard_stats(timespan, user=request.user)
        return Response({'data': stats, 'message': 'success'})
