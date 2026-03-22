from django.urls import path

from apps.workout.views import SessionDetailView, SessionListView

urlpatterns = [
    path('sessions/', SessionListView.as_view(), name='session-list'),
    path('sessions/<int:pk>/', SessionDetailView.as_view(), name='session-detail'),
]
