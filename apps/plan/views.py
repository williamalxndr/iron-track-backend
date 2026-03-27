from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .selectors import get_all_plan_weeklies, get_all_plans, get_plan_by_id, get_plan_weekly_by_id
from .serializers import (
    PlanDetailSerializer,
    PlanListSerializer,
    PlanWeeklyDetailSerializer,
    PlanWeeklyListSerializer,
)
from .services import create_plan, create_plan_weekly, delete_plan, update_plan


class PlanListView(APIView):
    def get(self, request):
        plans = get_all_plans(user=request.user)
        data = PlanListSerializer(plans, many=True).data
        return Response({'data': data, 'message': 'success'})

    def post(self, request):
        try:
            plan = create_plan(request.data, user=request.user)
        except ValueError as e:
            return Response(
                {'error': {'code': 'INVALID_REQUEST', 'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {'data': {'id': plan.id}, 'message': 'success'},
            status=status.HTTP_201_CREATED,
        )


class PlanDetailView(APIView):
    def get(self, request, pk):
        try:
            plan = get_plan_by_id(pk, user=request.user)
        except Exception:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Plan not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = PlanDetailSerializer(plan).data
        return Response({'data': data, 'message': 'success'})

    def put(self, request, pk):
        try:
            update_plan(pk, request.data, user=request.user)
        except ValueError as e:
            return Response(
                {'error': {'code': 'INVALID_REQUEST', 'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Plan not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'data': None, 'message': 'success'})

    def delete(self, request, pk):
        try:
            delete_plan(pk, user=request.user)
        except Exception:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Plan not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlanWeeklyListView(APIView):
    def get(self, request):
        weeklies = get_all_plan_weeklies(user=request.user)
        data = PlanWeeklyListSerializer(weeklies, many=True).data
        return Response({'data': data, 'message': 'success'})

    def post(self, request):
        try:
            weekly = create_plan_weekly(request.data, user=request.user)
        except ValueError as e:
            return Response(
                {'error': {'code': 'INVALID_REQUEST', 'message': str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {'data': {'id': weekly.id}, 'message': 'success'},
            status=status.HTTP_201_CREATED,
        )


class PlanWeeklyDetailView(APIView):
    def get(self, request, pk):
        try:
            weekly = get_plan_weekly_by_id(pk, user=request.user)
        except Exception:
            return Response(
                {'error': {'code': 'NOT_FOUND', 'message': 'Weekly plan not found'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = PlanWeeklyDetailSerializer(weekly).data
        return Response({'data': data, 'message': 'success'})
