from django.urls import path

from apps.plan.views import PlanDetailView, PlanListView, PlanWeeklyDetailView, PlanWeeklyListView

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plan-list'),
    path('plans/<int:pk>/', PlanDetailView.as_view(), name='plan-detail'),
    path('plan-weekly/', PlanWeeklyListView.as_view(), name='plan-weekly-list'),
    path('plan-weekly/<int:pk>/', PlanWeeklyDetailView.as_view(), name='plan-weekly-detail'),
]
