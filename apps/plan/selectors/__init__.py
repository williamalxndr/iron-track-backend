from django.db.models import Q

from apps.plan.models import Plan, PlanWeekly  # type: ignore


def get_all_plans(user):
    return Plan.objects.filter(Q(is_template=True) | Q(user=user))


def get_plan_by_id(plan_id, user):
    return Plan.objects.get(
        Q(id=plan_id),
        Q(is_template=True) | Q(user=user),
    )


def get_all_plan_weeklies(user):
    return PlanWeekly.objects.filter(Q(is_template=True) | Q(user=user))


def get_plan_weekly_by_id(plan_weekly_id, user):
    return PlanWeekly.objects.get(
        Q(id=plan_weekly_id),
        Q(is_template=True) | Q(user=user),
    )
