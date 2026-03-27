from django.urls import path

from . import views

urlpatterns = [
    path('plans/', views.PlanListView.as_view(), name='plan-list'),
    path('plans/<int:pk>/', views.PlanDetailView.as_view(), name='plan-detail'),
    path('plan-weekly/', views.PlanWeeklyListView.as_view(), name='plan-weekly-list'),
    path('plan-weekly/<int:pk>/', views.PlanWeeklyDetailView.as_view(), name='plan-weekly-detail'),
]
