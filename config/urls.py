from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.workout.urls')),
    path('api/v1/', include('apps.exercise.urls')),
    path('api/v1/', include('apps.plan.urls')),
    path('api/v1/', include('apps.sync.urls')),
]
