from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse

from .models import Documento, Usuario


class PermisosPorRolTests(TestCase):
	def crear_usuario(self, rol):
		return Usuario.objects.create(
			nombre=f'Usuario {rol}', correo=f'{rol.lower().replace(" ", "_")}@test.com',
			contrasena_hash=make_password('Clave123!'), rol=rol,
		)

	def iniciar_sesion(self, usuario):
		self.client.post(reverse('login'), {'correo': usuario.correo, 'contrasena': 'Clave123!'})

	def test_consultor_puede_ver_pero_no_crear_documentos(self):
		usuario = self.crear_usuario('Consultor')
		Documento.objects.create(nombre='Manual', codigo='DOC-1', version='1')
		self.iniciar_sesion(usuario)

		self.assertEqual(self.client.get(reverse('module_list', args=['documentos'])).status_code, 200)
		respuesta = self.client.get(reverse('module_create', args=['documentos']))
		self.assertRedirects(respuesta, reverse('dashboard'))

	def test_analista_puede_modificar_pero_no_eliminar(self):
		usuario = self.crear_usuario('Analista')
		documento = Documento.objects.create(nombre='Manual', codigo='DOC-1', version='1')
		self.iniciar_sesion(usuario)

		self.assertEqual(self.client.get(reverse('module_edit', args=['documentos', documento.pk])).status_code, 200)
		respuesta = self.client.post(reverse('module_delete', args=['documentos', documento.pk]))
		self.assertRedirects(respuesta, reverse('dashboard'))
		self.assertTrue(Documento.objects.filter(pk=documento.pk).exists())

	def test_consultor_no_puede_administrar_usuarios(self):
		usuario = self.crear_usuario('Consultor')
		self.iniciar_sesion(usuario)

		respuesta = self.client.get(reverse('module_list', args=['usuarios']))
		self.assertRedirects(respuesta, reverse('dashboard'))

	def test_administrador_puede_eliminar_documentos(self):
		usuario = self.crear_usuario('Administrador')
		documento = Documento.objects.create(nombre='Manual', codigo='DOC-1', version='1')
		self.iniciar_sesion(usuario)

		respuesta = self.client.post(reverse('module_delete', args=['documentos', documento.pk]))
		self.assertRedirects(respuesta, reverse('module_list', args=['documentos']))
		self.assertFalse(Documento.objects.filter(pk=documento.pk).exists())

	def test_consultor_puede_descargar_informe(self):
		usuario = self.crear_usuario('Consultor')
		self.iniciar_sesion(usuario)

		respuesta = self.client.get(reverse('descargar_reportes'))
		self.assertEqual(respuesta.status_code, 200)
		self.assertEqual(respuesta['Content-Type'], 'text/csv; charset=utf-8')
