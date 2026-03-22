from apps.plan.models import Plan


def get_all_plans():
    return Plan.objects.all()


def get_plan_by_id(plan_id):
    return Plan.objects.get(id=plan_id)
