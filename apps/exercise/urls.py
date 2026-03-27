from django.urls import path

from . import views

urlpatterns = [
    path('exercises/', views.ExerciseListView.as_view(), name='exercise-list'),
    path('exercises/<int:pk>/history/', views.ExerciseHistoryView.as_view(), name='exercise-history'),
    path('exercises/<int:pk>/stats/', views.ExerciseStatsView.as_view(), name='exercise-stats'),
]
