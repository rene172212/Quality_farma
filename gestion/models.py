from django.core.validators import FileExtensionValidator
from django.db import models


class Usuario(models.Model):
	ROLES = [
		('Administrador', 'Administrador'),
		('Analista', 'Analista'),
		('Consultor', 'Consultor'),
	]
	id_usuario = models.BigAutoField(primary_key=True)
	nombre = models.CharField(max_length=150)
	cargo = models.CharField(max_length=120, blank=True)
	area = models.CharField(max_length=120, blank=True)
	correo = models.EmailField(unique=True)
	contrasena_hash = models.CharField(max_length=255)
	rol = models.CharField(max_length=80, choices=ROLES, default='Consultor')
	estado = models.BooleanField(default=True)

	class Meta:
		db_table = 'usuario'
		ordering = ['nombre']


class Documento(models.Model):
	nombre = models.CharField(max_length=200)
	codigo = models.CharField(max_length=50)
	version = models.CharField(max_length=20)
	estado = models.CharField(max_length=50, default='Vigente')
	archivo = models.FileField(upload_to='documentos/', validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])], blank=True, null=True)
	subido_por = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='documentos_subidos')
	fecha_subida = models.DateTimeField(auto_now_add=True, null=True)
	fecha_creacion = models.DateField(auto_now_add=True)

	class Meta:
		db_table = 'documentos'
		ordering = ['-fecha_creacion', 'nombre']


class Hallazgo(models.Model):
	descripcion = models.TextField()
	area = models.CharField(max_length=120)
	responsable = models.CharField(max_length=150)
	estado = models.CharField(max_length=50, default='Abierto')
	fecha = models.DateField()

	class Meta:
		db_table = 'hallazgos'
		ordering = ['-fecha', '-id']


class Capa(models.Model):
	hallazgo = models.CharField(max_length=250)
	accion = models.TextField()
	responsable = models.CharField(max_length=150)
	estado = models.CharField(max_length=50, default='Pendiente')
	fecha = models.DateField()

	class Meta:
		db_table = 'capa'
		ordering = ['-fecha', '-id']


class Capacitacion(models.Model):
	nombre = models.CharField(max_length=200)
	responsable = models.CharField(max_length=150)
	participantes = models.CharField(max_length=50)
	estado = models.CharField(max_length=50, default='Programada')
	fecha = models.DateField()

	class Meta:
		db_table = 'capacitaciones'
		ordering = ['-fecha', '-id']
