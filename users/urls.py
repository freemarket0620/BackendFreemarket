#urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoriasViewSet,
    DetallesVentasViewSet,
    LoginView,
    PermisosViewSet,
    ProductosViewSet,
    RolesViewSet,
    UsuariosViewSet,
    UsuariosRolesViewSet,
    RolesPermisosViewSet,
    VentasViewSet,
)
from . import views
# Crea un router y registra tus ViewSets
router = DefaultRouter()
router.register(r'permisos', PermisosViewSet)
router.register(r'roles', RolesViewSet)
router.register(r'usuarios', UsuariosViewSet)
router.register(r'usuariosroles', UsuariosRolesViewSet)
router.register(r'rolespermisos', RolesPermisosViewSet)

# rutas de ventas 
router.register(r'categorias', CategoriasViewSet)  
router.register(r'productos', ProductosViewSet)    
router.register(r'ventas', VentasViewSet)
router.register(r'detallesventas', DetallesVentasViewSet) 


urlpatterns = [
    path('', include(router.urls)),  # Incluye las rutas generadas por el router
    path('login/', LoginView.as_view(), name='login'),  # Ruta para el inicio de sesión
]
