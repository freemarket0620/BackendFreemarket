#views.py
from datetime import timedelta
from confection import Config
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.db.models import Prefetch
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
import json
from cloudinary.uploader import upload
import cloudinary.uploader

from .models import Categorias, DetallesVentas, Permisos, Productos,  Roles,  Usuarios, RolesPermisos, UsuariosRoles, Ventas
from .serializers import   CategoriaSerializer,  DetallesVentasSerializer, PermisosSerializer,  ProductoSerializer, RolSerializer, RolesPermisosSerializer, UsuarioSerializer, LoginSerializer, UsuariosRolesSerializer, VentaSerializer


""" esto es la seccion de login """
# backend
class LoginView(APIView):
    authentication_classes = []  # Elimina autenticación solo para login
    permission_classes = []      # Deja vacía la lista de permisos

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        # Validación del formulario de login
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        correo = serializer.validated_data.get('correo')
        password = serializer.validated_data.get('password')

        try:
            usuario = Usuarios.objects.prefetch_related(
                Prefetch('usuariosroles_set', queryset=UsuariosRoles.objects.select_related('rol')),
                Prefetch('usuariosroles_set__rol__rolespermisos_set', queryset=RolesPermisos.objects.select_related('permiso'))
            ).get(correo=correo)

            # Verificación de estado del usuario
            if not usuario.estado_Usuario:
                return Response({
                    'error': 'No puedes iniciar sesión!!!. Comuníquese con el administrador. Gracias.'
                }, status=status.HTTP_403_FORBIDDEN)

            # Verificar la contraseña
            if not check_password(password, usuario.password):
                return Response({'error': 'Credenciales incorrectas'}, status=status.HTTP_400_BAD_REQUEST)

            # Generación del token JWT
            refresh = RefreshToken.for_user(usuario)
            access_token = str(refresh.access_token)

            # Obtener roles y permisos
            roles = [usuario_rol.rol.nombre_rol for usuario_rol in usuario.usuariosroles_set.all()]
            permisos = []
            for usuario_rol in usuario.usuariosroles_set.all():
                permisos += [rol_permiso.permiso.nombre_permiso for rol_permiso in usuario_rol.rol.rolespermisos_set.all()]

            # Verificar si el usuario tiene roles y permisos
            if not roles or not permisos:
                return Response({'error': 'El usuario no tiene roles ni permisos asignados.'}, status=status.HTTP_403_FORBIDDEN)

            # Respuesta de éxito
            return Response({
                'access_token': access_token,
                'roles': roles,
                'permisos': permisos,
                'nombre_usuario': usuario.nombre_usuario,  # Agregar nombre de usuario
                'apellido': usuario.apellido,              # Agregar apellido
                'imagen_url': usuario.imagen_url,            # Agregar URL de la imagen
                'usuario_id': usuario.id
            }, status=status.HTTP_200_OK)

        except Usuarios.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

# ViewSet for Permisos
class PermisosViewSet(viewsets.ModelViewSet):
    queryset = Permisos.objects.all()
    serializer_class = PermisosSerializer
    def create(self, request, *args, **kwargs):
        # Extraer datos del request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Valida los datos
        self.perform_create(serializer)  # Guarda el nuevo permiso
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = True  # Permite actualizaciones parciales
        instance = self.get_object()  # Obtiene la instancia del permiso a actualizar
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)  # Valida los datos
        self.perform_update(serializer)  # Actualiza el permiso
        return Response(serializer.data)
# ViewSet for Roles
class RolesViewSet(viewsets.ModelViewSet):
    queryset = Roles.objects.all()
    serializer_class = RolSerializer

    def create(self, request, *args, **kwargs):
        # Extraer datos del request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Valida los datos
        self.perform_create(serializer)  # Guarda el nuevo rol
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = True  # Permite actualizaciones parciales
        instance = self.get_object()  # Obtiene la instancia del rol a actualizar
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)  # Valida los datos
        self.perform_update(serializer)  # Actualiza el rol
        return Response(serializer.data)

# ViewSet for Usuarios
class UsuariosViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.all()
    serializer_class = UsuarioSerializer

    def create(self, request, *args, **kwargs):
        # Extraer datos del request
        data = {
            'nombre_usuario': request.data.get('nombre_usuario'),
            'apellido': request.data.get('apellido'),
            'telefono': request.data.get('telefono'),
            'correo': request.data.get('correo'),
            'password': request.data.get('password'),
            'ci': request.data.get('ci'),
            'ci_departamento': request.data.get('ci_departamento'),
            'fecha_nacimiento': request.data.get('fecha_nacimiento'),
        }

        # Subir la imagen a Cloudinary si se proporciona
        if 'imagen_url' in request.FILES:
            uploaded_image = cloudinary.uploader.upload(request.FILES['imagen_url'])
            data['imagen_url'] = uploaded_image.get('url')
            print("Uploaded Image URL:", data['imagen_url'])  # Debugging

        # Crear el usuario
        usuario = Usuarios.objects.create(**data)
        return Response(UsuarioSerializer(usuario).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = True  # Permite actualizaciones parciales
        instance = self.get_object()
        data = request.data.copy()  # Copia los datos del request

        # Si se proporciona una nueva imagen, subirla a Cloudinary
        if 'imagen_url' in request.FILES:
            uploaded_image = cloudinary.uploader.upload(request.FILES['imagen_url'])
            data['imagen_url'] = uploaded_image.get('url')

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
        
# ViewSet for UsuariosRoles
class UsuariosRolesViewSet(viewsets.ModelViewSet):
    queryset = UsuariosRoles.objects.all()
    serializer_class = UsuariosRolesSerializer

    def create(self, request, *args, **kwargs):
        usuario_id = request.data.get('usuario')
        rol_id = request.data.get('rol')

        if UsuariosRoles.objects.filter(usuario_id=usuario_id, rol_id=rol_id).exists():
            return Response({'error': ['El usuario ya tiene este rol asignado']}, status=status.HTTP_400_BAD_REQUEST)

        usuario_rol = UsuariosRoles.objects.create(usuario_id=usuario_id, rol_id=rol_id)
        return Response(UsuariosRolesSerializer(usuario_rol).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        instance = self.get_object()
        usuario_id = request.data.get('usuario', {}).get('id', instance.usuario_id)
        rol_id = request.data.get('rol', {}).get('id', instance.rol_id)

        if UsuariosRoles.objects.filter(usuario_id=usuario_id, rol_id=rol_id).exclude(pk=instance.pk).exists():
            return Response({'error': ['El usuario ya tiene este rol asignado']}, status=status.HTTP_400_BAD_REQUEST)

        instance.usuario_id = usuario_id
        instance.rol_id = rol_id
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# ViewSet for RolesPermisos

class RolesPermisosViewSet(viewsets.ModelViewSet):
    queryset = RolesPermisos.objects.all()
    serializer_class = RolesPermisosSerializer

    def create(self, request, *args, **kwargs):
        rol_id = request.data.get('rol')
        permiso_id = request.data.get('permiso')

        # Verificar si ya existe la relación entre rol y permiso
        if RolesPermisos.objects.filter(rol_id=rol_id, permiso_id=permiso_id).exists():
            return Response({'error': ['Este rol ya tiene este permiso asignado']}, status=status.HTTP_400_BAD_REQUEST)

        # Crear la relación
        roles_permisos = RolesPermisos.objects.create(rol_id=rol_id, permiso_id=permiso_id)
        return Response(RolesPermisosSerializer(roles_permisos).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        instance = self.get_object()
        rol_id = request.data.get('rol', {}).get('id', instance.rol_id)
        permiso_id = request.data.get('permiso', {}).get('id', instance.permiso_id)

        # Verificar si ya existe la relación entre rol y permiso, excluyendo la instancia actual
        if RolesPermisos.objects.filter(rol_id=rol_id, permiso_id=permiso_id).exclude(pk=instance.pk).exists():
            return Response({'error': ['Este rol ya tiene este permiso asignado']}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar la relación
        instance.rol_id = rol_id
        instance.permiso_id = permiso_id
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


""" seccion para las ventas  """
# ViewSet for Categorias
class CategoriasViewSet(viewsets.ModelViewSet):
    queryset = Categorias.objects.all()
    serializer_class = CategoriaSerializer
    def create(self, request, *args, **kwargs):
        # Extraer datos del request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Valida los datos
        self.perform_create(serializer)  # Guarda la nueva categoría
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = True  # Permite actualizaciones parciales
        instance = self.get_object()  # Obtiene la instancia de la categoría a actualizar
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)  # Valida los datos
        self.perform_update(serializer)  # Actualiza la categoría
        return Response(serializer.data)

class ProductosViewSet(viewsets.ModelViewSet):
    queryset = Productos.objects.all()
    serializer_class = ProductoSerializer

    def create(self, request, *args, **kwargs):
        # Extraer datos del request
        data = {
            'nombre_producto': request.data.get('nombre_producto'),
            'descripcion': request.data.get('descripcion'),
            'precio_compra': request.data.get('precio_compra'),
            'precio_unitario': request.data.get('precio_unitario'),
            'precio_mayor': request.data.get('precio_mayor'),
            'stock': request.data.get('stock'),
            'codigo_producto': request.data.get('codigo_producto'),
        }

        # Obtener la categoría como instancia de Categorias
        categoria_id = request.data.get('categoria')
        try:
            data['categoria'] = Categorias.objects.get(id=categoria_id)
        except Categorias.DoesNotExist:
            return Response({"error": "La categoría especificada no existe."}, status=status.HTTP_400_BAD_REQUEST)

        # Subir la imagen a Cloudinary si se proporciona
        if 'imagen_productos' in request.FILES:
            uploaded_image = cloudinary.uploader.upload(request.FILES['imagen_productos'])
            data['imagen_productos'] = uploaded_image.get('url')
            print("Uploaded Image URL:", data['imagen_productos'])  # Debugging line

        # Crear el producto
        producto = Productos.objects.create(**data)
        return Response(ProductoSerializer(producto).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        data = request.data.copy()

        # Subir nueva imagen si es necesario
        if 'imagen_productos' in request.FILES:
            uploaded_image = cloudinary.uploader.upload(request.FILES['imagen_productos'])
            data['imagen_productos'] = uploaded_image.get('url')

        # Manejo de categoría (actualización segura)
        categoria_data = request.data.get('categoria')
        if isinstance(categoria_data, str):
            categoria_data = json.loads(categoria_data)

        if isinstance(categoria_data, dict) and 'id' in categoria_data:
            instance.categoria_id = categoria_data['id']
        elif categoria_data:
            instance.categoria_id = categoria_data

        # Serializar los datos recibidos
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Realizar la actualización en la base de datos
        self.perform_update(serializer)

        return Response(serializer.data)



class VentasViewSet(viewsets.ModelViewSet):
    queryset = Ventas.objects.all()
    serializer_class = VentaSerializer

    def create(self, request, *args, **kwargs):
        # Extraer datos del request
        usuario_data = request.data.get('usuario')
        
        # Verificar si el usuario es un diccionario o un ID
        if isinstance(usuario_data, dict) and 'id' in usuario_data:
            usuario_id = usuario_data['id']
        else:
            usuario_id = usuario_data  # Asumir que es un ID

        # Validar que el usuario existe
        try:
            usuario = Usuarios.objects.get(id=usuario_id)
        except Usuarios.DoesNotExist:
            return Response({"error": "El usuario especificado no existe."}, status=status.HTTP_400_BAD_REQUEST)

        # Crear la venta
        data = {
            'usuario': usuario,
            'estado': request.data.get('estado', 'Pendiente'),
            'total': request.data.get('total'),
        }
        venta = Ventas.objects.create(**data)

        return Response(VentaSerializer(venta).data, status=status.HTTP_201_CREATED)
    
class DetallesVentasViewSet(viewsets.ModelViewSet):
    queryset = DetallesVentas.objects.all()
    serializer_class = DetallesVentasSerializer

    def create(self, request, *args, **kwargs):
        # Obtener el último registro de ventas
        try:
            ultima_venta = Ventas.objects.latest('id')  # Asumiendo que 'id' es el campo que se usa para ordenar
        except Ventas.DoesNotExist:
            return Response({"error": "No hay ventas registradas."}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el detalle de venta
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Asignar el ID de la última venta al detalle
            serializer.validated_data['venta'] = ultima_venta  # Asumiendo que 'venta' es el campo en DetallesVentas
            
            # Asegúrate de que el producto se esté asignando correctamente
            producto_id = request.data.get('producto_id')  # Asegúrate de que el ID del producto se esté enviando
            if producto_id:
                try:
                    producto = Productos.objects.get(id=producto_id)  # Cambia 'Producto' por 'Productos'
                    serializer.validated_data['producto'] = producto  # Asignar el producto
                except Productos.DoesNotExist:  # Cambia 'Producto' por 'Productos'
                    return Response({"error": "El producto especificado no existe."}, status=status.HTTP_400_BAD_REQUEST)

            detalle_venta = serializer.save()
            return Response(self.get_serializer(detalle_venta).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

