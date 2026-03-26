from django.urls import path

from apps.workout.views import DashboardView, SessionDetailView, SessionListView

urlpatterns = [
    path('sessions/dashboard/', DashboardView.as_view(), name='session-dashboard'),
    path('sessions/', SessionListView.as_view(), name='session-list'),
    path('sessions/<int:pk>/', SessionDetailView.as_view(), name='session-detail'),
]
