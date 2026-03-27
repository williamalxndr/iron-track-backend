from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer
from .services import create_user


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            user = create_user(request.data)
        except ValueError as e:
            return Response(
                {'error': {'code': 'INVALID_REQUEST', 'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {'data': {'id': user.id, 'username': user.username}, 'message': 'success'},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '')
        password = request.data.get('password', '')

        user = authenticate(username=username, password=password)
        if user is None:
            return Response(
                {'error': {'code': 'INVALID_CREDENTIALS', 'message': 'Invalid username or password'}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'data': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data,
                },
                'message': 'success',
            },
            status=status.HTTP_200_OK,
        )


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh', '')
        if not refresh_token:
            return Response(
                {'error': {'code': 'INVALID_REQUEST', 'message': 'Refresh token is required'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            old_refresh = RefreshToken(refresh_token)
            from apps.accounts.models import User  # type: ignore  # noqa: E402

            user = User.objects.get(id=old_refresh['user_id'])
            new_refresh = RefreshToken.for_user(user)
        except Exception:
            return Response(
                {'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired refresh token'}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                'data': {
                    'access': str(new_refresh.access_token),
                    'refresh': str(new_refresh),
                },
                'message': 'success',
            },
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {'data': UserSerializer(request.user).data, 'message': 'success'},
            status=status.HTTP_200_OK,
        )
