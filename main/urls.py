#urls.py  D:\2-2024\Tienda-Online\BackendDj\main\urls.py
from django.contrib import admin

from django.urls import path, include, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
]
