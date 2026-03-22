from django.urls import path

from apps.exercise.views import ExerciseListView

urlpatterns = [
    path('exercises/', ExerciseListView.as_view(), name='exercise-list'),
]
