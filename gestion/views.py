from functools import wraps
import csv

from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CapaForm, CapacitacionForm, DocumentoForm, HallazgoForm, LoginForm, UsuarioForm
from .models import Capa, Capacitacion, Documento, Hallazgo, Usuario


PERMISOS_ROL = {
	'Administrador': {'*': {'ver', 'crear', 'editar', 'eliminar'}},
	'Analista': {
		'documentos': {'ver', 'crear', 'editar'},
		'hallazgos': {'ver', 'crear', 'editar'},
		'capa': {'ver', 'crear', 'editar'},
		'capacitaciones': {'ver', 'crear', 'editar'},
		'reportes': {'ver'},
	},
	'Consultor': {
		'documentos': {'ver'},
		'hallazgos': {'ver'},
		'capa': {'ver'},
		'capacitaciones': {'ver'},
		'reportes': {'ver', 'descargar'},
	},
}


def rol_actual(request):
	return request.session.get('usuario_rol', 'Consultor')


def tiene_permiso(request, modulo, accion='ver'):
	permisos = PERMISOS_ROL.get(rol_actual(request), PERMISOS_ROL['Consultor'])
	return accion in permisos.get('*', set()) or accion in permisos.get(modulo, set())


def requiere_login(view):
	@wraps(view)
	def protegida(request, *args, **kwargs):
		if not request.session.get('usuario_id'):
			return redirect('login')
		return view(request, *args, **kwargs)
	return protegida


def requiere_permiso(modulo, accion='ver'):
	def decorador(view):
		@wraps(view)
		def protegida(request, *args, **kwargs):
			modulo_real = modulo or kwargs.get('module')
			if not request.session.get('usuario_id'):
				return redirect('login')
			if not tiene_permiso(request, modulo_real, accion):
				messages.error(request, 'No tienes permiso para realizar esta acción.')
				return redirect('dashboard')
			return view(request, *args, **kwargs)
		return protegida
	return decorador


def login_view(request):
	if request.session.get('usuario_id'):
		return redirect('dashboard')
	form = LoginForm(request.POST or None)
	error = None
	if request.method == 'POST' and form.is_valid():
		try:
			usuario = Usuario.objects.get(correo=form.cleaned_data['correo'], estado=True)
		except Usuario.DoesNotExist:
			usuario = None
		if usuario and check_password(form.cleaned_data['contrasena'], usuario.contrasena_hash):
			request.session['usuario_id'] = usuario.id_usuario
			request.session['usuario_nombre'] = usuario.nombre
			request.session['usuario_rol'] = usuario.rol
			return redirect('dashboard')
		error = 'Correo o contraseña incorrectos, o usuario inactivo.'
	return render(request, 'gestion/login.html', {'form': form, 'error': error})


def logout_view(request):
	request.session.flush()
	return redirect('login')


@requiere_login
def dashboard(request):
	totales = [
		('Usuarios', Usuario.objects.count(), 'usuarios'),
		('Documentos', Documento.objects.count(), 'documentos'),
		('Hallazgos', Hallazgo.objects.count(), 'hallazgos'),
		('CAPA', Capa.objects.count(), 'capa'),
		('Capacitaciones', Capacitacion.objects.count(), 'capacitaciones'),
	]
	return render(request, 'gestion/dashboard.html', {
		'totales': [total for total in totales if tiene_permiso(request, total[2])],
		'puede_reportes': tiene_permiso(request, 'reportes'),
	})


MODULES = {
	'usuarios': (Usuario, UsuarioForm, 'Usuarios', 'usuario'),
	'documentos': (Documento, DocumentoForm, 'Documentos de calidad', 'documento'),
	'hallazgos': (Hallazgo, HallazgoForm, 'Hallazgos', 'hallazgo'),
	'capa': (Capa, CapaForm, 'Acciones CAPA', 'capa'),
	'capacitaciones': (Capacitacion, CapacitacionForm, 'Capacitaciones', 'capacitacion'),
}


@requiere_permiso(None, 'ver')
def module_list(request, module):
	model, _, title, singular = MODULES[module]
	queryset = model.objects.all()
	query = request.GET.get('consulta', '').strip()
	if query and model is Capacitacion:
		queryset = queryset.filter(Q(nombre__icontains=query) | Q(responsable__icontains=query) | Q(estado__icontains=query))
	template = 'gestion/document_list.html' if module == 'documentos' else 'gestion/module_list.html'
	return render(request, template, {
		'items': queryset,
		'title': title,
		'module': module,
		'singular': singular,
		'query': query,
		'puede_crear': tiene_permiso(request, module, 'crear'),
		'puede_editar': tiene_permiso(request, module, 'editar'),
		'puede_eliminar': tiene_permiso(request, module, 'eliminar'),
	})


@requiere_permiso(None, 'crear')
def module_create(request, module):
	_, form_class, title, singular = MODULES[module]
	form = form_class(request.POST or None, request.FILES or None)
	if request.method == 'POST' and form.is_valid():
		item = form.save(commit=False)
		if module == 'documentos':
			item.subido_por_id = request.session.get('usuario_id')
		item.save()
		messages.success(request, 'Registro guardado correctamente.')
		return redirect('module_list', module=module)
	return render(request, 'gestion/form.html', {'form': form, 'title': f'Crear {singular}', 'module': module})


def siguiente_version(codigo):
	versiones = Documento.objects.filter(codigo=codigo).values_list('version', flat=True)
	versiones_numericas = [int(version) for version in versiones if str(version).isdigit()]
	proxima = max(versiones_numericas, default=0) + 1
	anchura = max((len(str(version)) for version in versiones if str(version).isdigit()), default=1)
	return str(proxima).zfill(anchura)


@requiere_permiso(None, 'editar')
def module_edit(request, module, pk):
	model, form_class, _, singular = MODULES[module]
	item = get_object_or_404(model, pk=pk)
	form = form_class(request.POST or None, request.FILES or None, instance=item)
	if request.method == 'POST' and form.is_valid():
		if module == 'documentos':
			item.estado = 'Anulado'
			item.save(update_fields=['estado'])
			nuevo = Documento(
				nombre=form.cleaned_data['nombre'],
				codigo=form.cleaned_data['codigo'],
				version=siguiente_version(form.cleaned_data['codigo']),
				estado=form.cleaned_data['estado'],
				subido_por_id=request.session.get('usuario_id'),
			)
			archivo = form.cleaned_data.get('archivo')
			nuevo.archivo = archivo if archivo else item.archivo.name if item.archivo else None
			nuevo.save()
			messages.success(request, f'Nueva versión {nuevo.version} creada correctamente.')
		else:
			form.save()
			messages.success(request, 'Registro actualizado correctamente.')
		return redirect('module_list', module=module)
	return render(request, 'gestion/form.html', {'form': form, 'title': f'Editar {singular}', 'module': module})


@requiere_permiso(None, 'eliminar')
def module_delete(request, module, pk):
	model, _, _, _ = MODULES[module]
	item = get_object_or_404(model, pk=pk)
	if request.method == 'POST':
		item.delete()
		messages.success(request, 'Registro eliminado correctamente.')
	return redirect('module_list', module=module)


@requiere_permiso('reportes')
def reportes(request):
	groups = [('Documentos por estado', Documento), ('Hallazgos por estado', Hallazgo), ('CAPA por estado', Capa), ('Capacitaciones por estado', Capacitacion)]
	resumenes = [(title, model.objects.values('estado').annotate(total=Count('id')).order_by('-total', 'estado')) for title, model in groups]
	recientes = [
		('Documentos recientes', [{'nombre': row.nombre, 'estado': row.estado, 'fecha': row.fecha_creacion} for row in Documento.objects.all()[:5]]),
		('Hallazgos recientes', [{'nombre': row.descripcion, 'estado': row.estado, 'fecha': row.fecha} for row in Hallazgo.objects.all()[:5]]),
		('Acciones CAPA recientes', [{'nombre': row.accion, 'estado': row.estado, 'fecha': row.fecha} for row in Capa.objects.all()[:5]]),
		('Capacitaciones recientes', [{'nombre': row.nombre, 'estado': row.estado, 'fecha': row.fecha} for row in Capacitacion.objects.all()[:5]]),
	]
	return render(request, 'gestion/reportes.html', {'resumenes': resumenes, 'recientes': recientes})


@requiere_permiso('reportes', 'descargar')
def descargar_reportes(request):
	respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
	respuesta['Content-Disposition'] = 'attachment; filename="informe_quality_farma.csv"'
	escritor = csv.writer(respuesta)
	escritor.writerow(['Informe Quality Farma'])
	escritor.writerow(['Modulo', 'Estado', 'Total'])
	for title, model in [('Documentos', Documento), ('Hallazgos', Hallazgo), ('CAPA', Capa), ('Capacitaciones', Capacitacion)]:
		for fila in model.objects.values('estado').annotate(total=Count('id')).order_by('-total', 'estado'):
			escritor.writerow([title, fila['estado'], fila['total']])
	return respuesta
