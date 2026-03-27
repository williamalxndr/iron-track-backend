from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User

TEST_PASSWORD = 'testpass123'  # noqa: S105


class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_success(self):
        resp = self.client.post(
            '/api/v1/auth/register/',
            {
                'username': 'newuser',
                'email': 'new@test.com',
                'password': 'testpass123',
                'first_name': 'New',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['data']['username'], 'newuser')
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_duplicate_username(self):
        User.objects.create_user(username='taken', password=TEST_PASSWORD)
        resp = self.client.post(
            '/api/v1/auth/register/',
            {
                'username': 'taken',
                'password': 'testpass123',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_short_password(self):
        resp = self.client.post(
            '/api/v1/auth/register/',
            {
                'username': 'user1',
                'password': 'short',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_username(self):
        resp = self.client.post(
            '/api/v1/auth/register/',
            {
                'password': 'testpass123',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password=TEST_PASSWORD,
            first_name='Test',
        )

    def test_login_success(self):
        resp = self.client.post(
            '/api/v1/auth/login/',
            {
                'username': 'testuser',
                'password': 'testpass123',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data['data'])
        self.assertIn('refresh', resp.data['data'])
        self.assertEqual(resp.data['data']['user']['username'], 'testuser')

    def test_login_bad_credentials(self):
        resp = self.client.post(
            '/api/v1/auth/login/',
            {
                'username': 'testuser',
                'password': 'wrong',
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class RefreshViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password=TEST_PASSWORD)

    def test_refresh_success(self):
        refresh = RefreshToken.for_user(self.user)
        resp = self.client.post('/api/v1/auth/refresh/', {'refresh': str(refresh)})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data['data'])
        self.assertIn('refresh', resp.data['data'])

    def test_refresh_invalid_token(self):
        resp = self.client.post('/api/v1/auth/refresh/', {'refresh': 'invalid'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_missing_token(self):
        resp = self.client.post('/api/v1/auth/refresh/', {})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class MeViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password=TEST_PASSWORD,
            first_name='Test',
            email='test@test.com',
        )

    def test_me_authenticated(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get('/api/v1/auth/me/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['data']['username'], 'testuser')
        self.assertEqual(resp.data['data']['first_name'], 'Test')

    def test_me_unauthenticated(self):
        resp = self.client.get('/api/v1/auth/me/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
