from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from datetime import date

from gestion.models import Capa, Capacitacion, Documento, Hallazgo, Usuario


class Command(BaseCommand):
    help = 'Carga un usuario administrador y datos demo de Quality Farma.'

    def handle(self, *args, **options):
        Usuario.objects.update_or_create(
            correo='raczooscar172212@gmail.com',
            defaults={'nombre': 'Administrador Quality Farma', 'cargo': 'Administrador', 'area': 'Calidad', 'rol': 'Administrador', 'estado': True, 'contrasena_hash': make_password('admin')},
        )
        for nombre, codigo, version, estado in [
            ('Procedimiento recepción de medicamentos', 'POE-001', '02', 'Vigente'),
            ('Procedimiento almacenamiento cadena fría', 'POE-002', '03', 'Vigente'),
            ('Manual sistema gestión calidad', 'MAN-001', '01', 'Vigente'),
        ]:
            Documento.objects.get_or_create(codigo=codigo, defaults={'nombre': nombre, 'version': version, 'estado': estado})
        Hallazgo.objects.get_or_create(descripcion='Registro de temperatura incompleto en almacenamiento', defaults={'area': 'Almacenamiento', 'responsable': 'Coordinador Calidad', 'estado': 'Cerrado', 'fecha': date(2026, 8, 1)})
        Capa.objects.get_or_create(hallazgo='Registro temperatura incompleto', defaults={'accion': 'Implementar verificación diaria registros', 'responsable': 'Coordinador Calidad', 'estado': 'Completada', 'fecha': date(2026, 8, 15)})
        Capacitacion.objects.get_or_create(nombre='Buenas prácticas almacenamiento', defaults={'responsable': 'Coordinador Calidad', 'participantes': '15', 'estado': 'Realizada', 'fecha': date(2026, 8, 1)})
        self.stdout.write(self.style.SUCCESS('Datos demo cargados. Usuario: raczooscar172212@gmail.com / admin'))
