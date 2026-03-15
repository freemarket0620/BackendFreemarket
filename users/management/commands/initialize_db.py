from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from users.models import Roles, Permisos, Usuarios, UsuariosRoles, RolesPermisos
from datetime import date
# Targetas

class Command(BaseCommand):
    help = "Inicializa la base de datos con datos básicos"

    def handle(self, *args, **kwargs):

        self.stdout.write("Inicializando base de datos...")

        # ==================================================
        # CREAR ROLES
        # ==================================================

        admin_role, _ = Roles.objects.get_or_create(
            nombre_rol="Administrador",
            defaults={"estado_Rol": True},
        )

        vendedor_role, _ = Roles.objects.get_or_create(
            nombre_rol="Vendedor",
            defaults={"estado_Rol": True},
        )

        # ==================================================
        #  CREAR PERMISOS
        # ==================================================

        permisos_data = [

            {"nombre_permiso": "registrarUsuarios", "descripcion": "Permite registrar usuarios"},
            {"nombre_permiso": "registrarRoles", "descripcion": "Permite registrar roles"},
            {"nombre_permiso": "registrarPermisos", "descripcion": "Permite registrar permisos"},
            {"nombre_permiso": "registrarUsuarioRoles", "descripcion": "Asignar roles a usuarios"},
            {"nombre_permiso": "registrarRolesPermisos", "descripcion": "Asignar permisos a roles"},

            {"nombre_permiso": "registrarCategorias", "descripcion": "Gestionar categorías"},
            {"nombre_permiso": "registrarProductos", "descripcion": "Gestionar productos"},

            {"nombre_permiso": "registrarVenta", "descripcion": "Registrar ventas"},
            {"nombre_permiso": "registrarDetalleVenta", "descripcion": "Registrar detalle de ventas"},

            {"nombre_permiso": "registrarVenta-Empleado", "descripcion": "Empleado puede registrar ventas"},
            {"nombre_permiso": "registrarVenta-DetalleVenta-Empleado", "descripcion": "Empleado puede vender productos"},

            {"nombre_permiso": "registrarVenta-DetalleVenta-Administrador", "descripcion": "Administrador puede vender con detalle"},

            {"nombre_permiso": "RegistrarJuegos", "descripcion": "Registrar juegos"},
            {"nombre_permiso": "VenderJugos", "descripcion": "Vender juegos"},

            {"nombre_permiso": "Efectivo", "descripcion": "Control de efectivo"},
            {"nombre_permiso": "Prestamos", "descripcion": "Control de prestamos"},
        ]

        permisos_objects = []

        for permiso in permisos_data:

            p, _ = Permisos.objects.get_or_create(
                nombre_permiso=permiso["nombre_permiso"],
                defaults={
                    "descripcion": permiso.get("descripcion", ""),
                    "estado_Permiso": True,
                },
            )

            permisos_objects.append(p)

        # ==================================================
        #  CREAR USUARIO ADMIN
        # ==================================================

        admin_user, created = Usuarios.objects.get_or_create(
            ci="13247291",
            defaults={
                "nombre_usuario": "Andres Benito",
                "apellido": "Yucra",
                "fecha_nacimiento": date(1998, 11, 6),
                "telefono": "72937437",
                "correo": "benitoandrescalle035@gmail.com",
                "password": make_password("Andres1234*"),
                "ci_departamento": "LP",
                "estado_Usuario": True,
                "imagen_url": "",
            },
        )

        if created:
            self.stdout.write(f"Usuario administrador creado: {admin_user}")

        UsuariosRoles.objects.get_or_create(
            usuario=admin_user,
            rol=admin_role
        )

        # ==================================================
        #  CREAR USUARIO VENDEDOR
        # ==================================================

        vendedor_user, created = Usuarios.objects.get_or_create(
            ci="9999999",
            defaults={
                "nombre_usuario": "Usuario",
                "apellido": "Vendedor",
                "fecha_nacimiento": date(2000, 1, 1),
                "telefono": "74905554",
                "correo": "freemarket0620@gmail.com",
                "password": make_password("Free1234*"),
                "ci_departamento": "LP",
                "estado_Usuario": True,
                "imagen_url": "",
            },
        )

        if created:
            self.stdout.write(f"Usuario vendedor creado: {vendedor_user}")

        UsuariosRoles.objects.get_or_create(
            usuario=vendedor_user,
            rol=vendedor_role
        )

        # ==================================================
        #  PERMISOS ADMIN (TODOS)
        # ==================================================

        for permiso in permisos_objects:

            RolesPermisos.objects.get_or_create(
                rol=admin_role,
                permiso=permiso
            )

        # ==================================================
        # PERMISOS VENDEDOR
        # ==================================================

        permisos_vendedor = [
            "registrarDetalleVenta",
            "registrarVenta-DetalleVenta-Empleado",
            "Efectivo",
        ]

        for permiso in permisos_objects:

            if permiso.nombre_permiso in permisos_vendedor:

                RolesPermisos.objects.get_or_create(
                    rol=vendedor_role,
                    permiso=permiso
                )

        # ==================================================
        # FINAL
        # ==================================================

        self.stdout.write(
            self.style.SUCCESS("Base de datos inicializada exitosamente!")
        )

        """
        PASO 1
        python manage.py initialize_db

        PASO 2
        python manage.py runserver
        """