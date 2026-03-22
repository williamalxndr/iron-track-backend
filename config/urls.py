from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('health/', health_check),
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.workout.urls')),
    path('api/v1/', include('apps.exercise.urls')),
    path('api/v1/', include('apps.plan.urls')),
    path('api/v1/', include('apps.sync.urls')),
]
