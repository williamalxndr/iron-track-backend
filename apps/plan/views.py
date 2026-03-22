from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.plan.models import Plan, PlanWeekly
from apps.plan.selectors import get_all_plan_weeklies, get_all_plans, get_plan_by_id, get_plan_weekly_by_id
from apps.plan.serializers import (
    PlanDetailSerializer,
    PlanListSerializer,
    PlanWeeklyDetailSerializer,
    PlanWeeklyListSerializer,
)
from apps.plan.services import create_plan


class PlanListView(APIView):
    def get(self, request):
        plans = get_all_plans()
        serializer = PlanListSerializer(plans, many=True)
        return Response({'data': serializer.data, 'message': 'success'})

    def post(self, request):
        try:
            plan = create_plan(request.data)
        except ValueError as e:
            return Response(
                {'error': {'code': 'INVALID_REQUEST', 'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'data': {'id': plan.id}, 'message': 'success'}, status=status.HTTP_201_CREATED)


class PlanDetailView(APIView):
    def get(self, request, pk):
        try:
            plan = get_plan_by_id(pk)
        except Plan.DoesNotExist:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Plan not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PlanDetailSerializer(plan)
        return Response({'data': serializer.data, 'message': 'success'})


class PlanWeeklyListView(APIView):
    def get(self, request):
        weeklies = get_all_plan_weeklies()
        serializer = PlanWeeklyListSerializer(weeklies, many=True)
        return Response({'data': serializer.data, 'message': 'success'})


class PlanWeeklyDetailView(APIView):
    def get(self, request, pk):
        try:
            weekly = get_plan_weekly_by_id(pk)
        except PlanWeekly.DoesNotExist:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Weekly plan not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PlanWeeklyDetailSerializer(weekly)
        return Response({'data': serializer.data, 'message': 'success'})
