# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views_usuarios, views_produtos


# Crea un router y registra tus ViewSets
router = DefaultRouter()
router.register(r"permisos", views_usuarios.PermisosViewSet)
router.register(r"roles", views_usuarios.RolesViewSet)
router.register(r"usuarios", views_usuarios.UsuariosViewSet)
router.register(r"usuariosroles", views_usuarios.UsuariosRolesViewSet)
router.register(r"rolespermisos", views_usuarios.RolesPermisosViewSet)

# rutas de ventas
router.register(r"categorias", views_produtos.CategoriasViewSet)
router.register(r"productos", views_produtos.ProductosViewSet)
router.register(r"ventas", views_produtos.VentasViewSet)
router.register(r"detallesventas", views_produtos.DetallesVentasViewSet)

# rutas de ventas de jeugos
router.register(r"RecargaProducto", views_produtos.RecargaProductoViewSet)
router.register(r"DetalleVentaRecarga", views_produtos.DetalleVentaRecargaViewSet)

# rutas de nuevas tablas
router.register(r"efectivo", views_produtos.EfectivoViewSet)
router.register(r"recarga-max", views_produtos.RecargaMaxViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("login/", views_usuarios.LoginView.as_view(), name="login"),
]
