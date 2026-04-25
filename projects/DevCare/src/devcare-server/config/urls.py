from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('user.urls')),
    path('api/rehab/', include('rehab.urls')),
    path('api/ai/', include('ai_module.urls')),
]
