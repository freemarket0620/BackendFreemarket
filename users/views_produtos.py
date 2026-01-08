# views.py
from datetime import datetime
import pytz
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
import json
from cloudinary.uploader import upload
import cloudinary.uploader

from .models import (
    Categorias,
    DetalleVentaRecarga,
    DetallesVentas,
    Productos,
    RecargaProducto,
    Usuarios,
    Ventas,
)
from .serializers import (
    CategoriaSerializer,
    DetalleVentaRecargaSerializer,
    DetallesVentasSerializer,
    ProductoSerializer,
    RecargaProductoSerializer,
    VentaSerializer,
)
from django.shortcuts import get_object_or_404

""" seccion para las ventas  """


class CategoriasViewSet(viewsets.ModelViewSet):
    queryset = Categorias.objects.all()
    serializer_class = CategoriaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Valida los datos
        self.perform_create(serializer)  # Guarda la nueva categoría
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = True  # Permite actualizaciones parciales
        instance = (
            self.get_object()
        )  # Obtiene la instancia de la categoría a actualizar
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)  # Valida los datos
        self.perform_update(serializer)  # Actualiza la categoría
        return Response(serializer.data)


class ProductosViewSet(viewsets.ModelViewSet):
    queryset = Productos.objects.all()
    serializer_class = ProductoSerializer

    def create(self, request, *args, **kwargs):
        data = {
            "nombre_producto": request.data.get("nombre_producto"),
            "descripcion": request.data.get("descripcion"),
            "precio_compra": request.data.get("precio_compra"),
            "precio_unitario": request.data.get("precio_unitario"),
            "precio_mayor": request.data.get("precio_mayor"),
            "stock": request.data.get("stock"),
            "codigo_producto": request.data.get("codigo_producto"),
        }
        categoria_id = request.data.get("categoria")
        try:
            data["categoria"] = Categorias.objects.get(id=categoria_id)
        except Categorias.DoesNotExist:
            return Response(
                {"error": "La categoría especificada no existe."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if "imagen_productos" in request.FILES:
            uploaded_image = cloudinary.uploader.upload(
                request.FILES["imagen_productos"]
            )
            data["imagen_productos"] = uploaded_image.get("url")
            print("Uploaded Image URL:", data["imagen_productos"])  # Debugging line
        producto = Productos.objects.create(**data)
        return Response(
            ProductoSerializer(producto).data, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        data = request.data.copy()
        if "imagen_productos" in request.FILES:
            uploaded_image = cloudinary.uploader.upload(
                request.FILES["imagen_productos"]
            )
            data["imagen_productos"] = uploaded_image.get("url")

        categoria_data = request.data.get("categoria")
        if isinstance(categoria_data, str):
            categoria_data = json.loads(categoria_data)

        if isinstance(categoria_data, dict) and "id" in categoria_data:
            instance.categoria_id = categoria_data["id"]
        elif categoria_data:
            instance.categoria_id = categoria_data

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        return Response(serializer.data)


class VentasViewSet(viewsets.ModelViewSet):
    queryset = Ventas.objects.all()
    serializer_class = VentaSerializer

    def create(self, request, *args, **kwargs):
        usuario_data = request.data.get("usuario")

        if isinstance(usuario_data, dict) and "id" in usuario_data:
            usuario_id = usuario_data["id"]
        else:
            usuario_id = usuario_data  # Asumir que es un ID

        try:
            usuario = Usuarios.objects.get(id=usuario_id)
        except Usuarios.DoesNotExist:
            return Response(
                {"error": "El usuario especificado no existe."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        local_tz = pytz.timezone("America/La_Paz")  # Zona horaria de Bolivia
        fecha_venta = datetime.now(local_tz)  # Obtener la hora local directamente

        data = {
            "usuario": usuario,
            "estado": request.data.get("estado", "Pendiente"),
            "total": request.data.get(
                "total", 0.00
            ),  # Asegúrate de que el total tenga un valor por defecto
            "fecha_venta": fecha_venta,  # Este campo se manejará automáticamente en el modelo
        }
        venta = Ventas.objects.create(**data)

        return Response(VentaSerializer(venta).data, status=status.HTTP_201_CREATED)


class DetallesVentasViewSet(viewsets.ModelViewSet):
    queryset = DetallesVentas.objects.all()
    serializer_class = DetallesVentasSerializer

    def create(self, request, *args, **kwargs):
        # Obtener el último registro de ventas
        try:
            ultima_venta = Ventas.objects.latest(
                "id"
            )  # Asumiendo que 'id' es el campo que se usa para ordenar
        except Ventas.DoesNotExist:
            return Response(
                {"error": "No hay ventas registradas."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Crear el detalle de venta
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Asignar el ID de la última venta al detalle
            serializer.validated_data["venta"] = (
                ultima_venta  # Asumiendo que 'venta' es el campo en DetallesVentas
            )

            # Asegúrate de que el producto se esté asignando correctamente
            producto_id = request.data.get(
                "producto_id"
            )  # Asegúrate de que el ID del producto se esté enviando
            if producto_id:
                try:
                    producto = Productos.objects.get(
                        id=producto_id
                    )  # Cambia 'Producto' por 'Productos'
                    serializer.validated_data["producto"] = (
                        producto  # Asignar el producto
                    )
                except Productos.DoesNotExist:  # Cambia 'Producto' por 'Productos'
                    return Response(
                        {"error": "El producto especificado no existe."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            detalle_venta = serializer.save()
            return Response(
                self.get_serializer(detalle_venta).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


""" nueva seccion   de vnetas de juegos """


class RecargaProductoViewSet(viewsets.ModelViewSet):
    queryset = RecargaProducto.objects.all()
    serializer_class = RecargaProductoSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        categoria_id = request.data.get("categoria")
        try:
            data["categoria"] = get_object_or_404(Categorias, id=categoria_id)
        except:
            return Response(
                {"error": "La categoría especificada no existe."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recarga = RecargaProducto.objects.create(**data)
        return Response(
            RecargaProductoSerializer(recarga).data, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        data = request.data.copy()
        categoria_id = request.data.get("categoria")
        if categoria_id:
            instance.categoria = get_object_or_404(Categorias, id=categoria_id)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class DetalleVentaRecargaViewSet(viewsets.ModelViewSet):
    queryset = DetalleVentaRecarga.objects.all()
    serializer_class = DetalleVentaRecargaSerializer

    def create(self, request, *args, **kwargs):
        # Tomamos la última venta si no se envía
        if "venta" not in request.data:
            try:
                ultima_venta = Ventas.objects.latest("id")
                request.data["venta"] = ultima_venta.id
            except Ventas.DoesNotExist:
                return Response({"error": "No hay ventas registradas."}, status=400)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Calcular precio y subtotal automáticamente
        recarga = serializer.validated_data["recarga"]
        cantidad = serializer.validated_data["cantidad"]
        serializer.validated_data["precio"] = recarga.precio_venta
        serializer.validated_data["subtotal"] = cantidad * recarga.precio_venta

        detalle = serializer.save()
        return Response(self.get_serializer(detalle).data, status=201)

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
