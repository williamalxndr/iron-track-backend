from apps.plan.models import Plan, PlanWeekly


def get_all_plans():
    return Plan.objects.all()


def get_plan_by_id(plan_id):
    return Plan.objects.get(id=plan_id)


def get_all_plan_weeklies():
    return PlanWeekly.objects.all()


def get_plan_weekly_by_id(plan_weekly_id):
    return PlanWeekly.objects.get(id=plan_weekly_id)
