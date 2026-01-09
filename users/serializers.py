# serializers
from rest_framework import serializers
from .models import (
    Categorias,
    DetalleVentaRecarga,
    DetallesVentas,
    Efectivo,
    Productos,
    RecargaMax,
    RecargaProducto,
    Usuarios,
    Roles,
    Permisos,
    UsuariosRoles,
    RolesPermisos,
    Ventas,
)


class LoginSerializer(serializers.Serializer):
    correo = serializers.EmailField(max_length=100, required=False, allow_null=True)
    password = serializers.CharField(max_length=255, required=True)


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = "__all__"


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = "__all__"


class PermisosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permisos
        fields = "__all__"


class UsuariosRolesSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    rol = RolSerializer(read_only=True)

    class Meta:
        model = UsuariosRoles
        fields = "__all__"


class RolesPermisosSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True)
    permiso = PermisosSerializer(read_only=True)

    class Meta:
        model = RolesPermisos
        fields = "__all__"


""" seccion de ventas tienda """


# Serializers para la sección de ventas
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias
        fields = "__all__"


class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)

    class Meta:
        model = Productos
        fields = "__all__"


class VentaSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Ventas
        fields = "__all__"


class DetallesVentasSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    venta = VentaSerializer(read_only=True)

    class Meta:
        model = DetallesVentas
        fields = "__all__"


# Serializers para recargas de videojuegos
class RecargaProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)

    class Meta:
        model = RecargaProducto
        fields = "__all__"


class DetalleVentaRecargaSerializer(serializers.ModelSerializer):
    recarga = RecargaProductoSerializer(read_only=True)

    class Meta:
        model = DetalleVentaRecarga
        fields = "__all__"


class EfectivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Efectivo
        fields = "__all__"


class RecargaMaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecargaMax
        fields = "__all__"
