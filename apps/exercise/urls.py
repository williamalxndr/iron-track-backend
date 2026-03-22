from django.urls import path

from apps.exercise.views import ExerciseHistoryView, ExerciseListView, ExerciseStatsView

urlpatterns = [
    path('exercises/', ExerciseListView.as_view(), name='exercise-list'),
    path('exercises/<int:pk>/history/', ExerciseHistoryView.as_view(), name='exercise-history'),
    path('exercises/<int:pk>/stats/', ExerciseStatsView.as_view(), name='exercise-stats'),
]
